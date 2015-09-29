# pylint: disable=import-error
from django.template import Template, Context
import logging
import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, Reference
from xblock.fragment import Fragment
from xblock.validation import ValidationMessage

from submissions import api as sub_api  # installed from the edx-submissions repository

try:
    from courseware.grades import get_score
    from courseware.module_utils import yield_dynamic_descriptor_descendents
    from student.models import user_by_anonymous_id
    EDX_FOUND = True
except ImportError:
    EDX_FOUND = False

import pkg_resources
import requests

from urlparse import urlparse

def normalize_id(key):
    """
    Helper method to normalize a key to avoid issues where some keys have version/branch and others don't.
    e.g. self.scope_ids.usage_id != self.runtime.get_block(self.scope_ids.usage_id).scope_ids.usage_id
    """
    if hasattr(key, "for_branch"):
        key = key.for_branch(None)
    if hasattr(key, "for_version"):
        key = key.for_version(None)
    return key

class AssessmentEndcapXBlock(XBlock):
    """
    An XBlock that gives feedback to users after they finish an assessment
    """

    graded_target_id = Reference(
        scope=Scope.settings,
        help="Which graded component to use as the basis of the leaderboard.",
    )

    CSS_FILE = "static/css/leaderboard.css"

    def author_view(self, context=None):
        graded_target_name = self.graded_target_id
        graded_target = self.runtime.get_block(self.graded_target_id) if self.graded_target_id else None
        if graded_target:
            graded_target_name = getattr(graded_target, "display_name", graded_target_name)
        return self.create_fragment(
            "static/html/assessmentendcap_studio.html",
            context={
                'graded_target_id': self.graded_target_id,
                'graded_target_name': graded_target_name,
                'display_name': self.display_name,
            },
        )

    def studio_view(self, context=None):
        """
        Display the form for changing this XBlock's settings.
        """
        own_id = normalize_id(self.scope_ids.usage_id)  # Normalization needed in edX Studio :-/

        flat_block_tree = []

        def build_tree(block, ancestors):
            """
            Build up a tree of information about the XBlocks descending from root_block
            """
            block_name = getattr(block, "display_name", None)
            if not block_name:
                block_type = block.runtime.id_reader.get_block_type(block.scope_ids.def_id)
                block_name = "{} ({})".format(block_type, block.scope_ids.usage_id)
            eligible = getattr(block, "has_score", False)
            if eligible:
                # If this block is graded, we mark all its ancestors as gradeable too
                if ancestors and not ancestors[-1]["eligible"]:
                    for ancestor in ancestors:
                        ancestor["eligible"] = True
            block_id = normalize_id(block.scope_ids.usage_id)
            new_entry = {
                "depth": len(ancestors),
                "id": block_id,
                "name": block_name,
                "eligible": eligible,
                "is_this": block_id == own_id,
            }
            flat_block_tree.append(new_entry)
            if block.has_children and not getattr(block, "has_dynamic_children", lambda: False)():
                for child_id in block.children:
                    build_tree(block.runtime.get_block(child_id), ancestors=(ancestors + [new_entry]))

        # Determine the root block and build the tree from its immediate children.
        # We don't include the root (course) block because it has too complex a
        # grading calculation and it's not required for intended uses of this block.
        root_block = self
        while root_block.parent:
            root_block = root_block.get_parent()
        for child_id in root_block.children:
            build_tree(root_block.runtime.get_block(child_id), [])

        return self.create_fragment(
            "static/html/assessmentendcap_studio_edit.html",
            context={
                'graded_target_id': self.graded_target_id,
                'block_tree': flat_block_tree,
            },
            javascript=["static/js/leaderboard_studio.js", "static/js/grade_leaderboard_studio.js"],
            initialize='GradeLeaderboardStudioXBlock'
        )


    def student_view(self, context):
        """
        Create a fragment used to display the XBlock to a student.
        `context` is a dictionary used to configure the display (unused).

        Returns a `Fragment` object specifying the HTML, CSS, and JavaScript
        to display.
        """

        attempts = None
        max_attempts = None
        score = None
        passing = False
        is_attempted = False

        # On first adding the block, the studio calls student_view instead of
        # author_view, which causes problems. Force call of the author view.
        if getattr(self.runtime, 'is_author_mode', False):
            return self.author_view()

        if EDX_FOUND:


            total_correct, total_possible = 0, 0

            target_block_id = self.graded_target_id
            course_id = target_block_id.course_key.for_branch(None).version_agnostic()

            target_block = self.runtime.get_block(target_block_id)

            student = user_by_anonymous_id(self.runtime.anonymous_student_id)

            count = 0


            if student:
                def create_module(descriptor):
                    return target_block.runtime.get_block(descriptor.location)

                for module_descriptor in yield_dynamic_descriptor_descendents(target_block, create_module):

                    (correct, total) = get_score(course_id, student, module_descriptor, create_module)
                    if (correct is None and total is None) or (not total > 0):
                       continue

                    # Note we ignore the 'graded' flag since authors may wish to use a leaderboard for non-graded content
                    total_correct += correct
                    total_possible += total
                    count += 1

                    attempts = module_descriptor.problem_attempts
                    max_attempts = module_descriptor.max_attempts

                    is_attempted =  module_descriptor.is_attempted
                    embed_code = module_descriptor.get_problem_html
            else:
                embed_code = "aaaa"
        else:
            embed_code = "Error: EdX not found."

        #lets do some math to see if we passed
        score = 0
        # calculate score
        passing = False
        if total_possible > 0:
            score = total_correct / total_possible * 100 #get score out of 100, not 1
        if score >= 80:
            passing = True

        if attempts > 0 or is_attempted == True:
            # student has submitted this assessment
            result_file="assessmentendcap.html"

            if passing:
                result_file = "assessmentendcap-pass.html"
            else:
                if max_attempts and attempts < max_attempts:
                    # student can still submit this problem again
                    result_file = "assessmentendcap-tryagain.html"

                elif attempts >= max_attempts:
                    # student has submitted this problem the max number of times
                    result_file = "assessmentendcap-fail.html"

        else:
            #student has not submitted assessment. We don't need to render anything.
            result_file="assessmentendcap-blank.html"

        return self.create_fragment(
            "static/html/" + result_file,
            context={
                'embed_code': embed_code,
                'total_correct': total_correct,
                'total_possible': total_possible,
                'score': score,
                'attempts': attempts,
                'max_attempts': max_attempts,
                'count' : count,
                'is_attempted': is_attempted
            },
            javascript=["static/js/assessmentendcap.js"],
            initialize='AssessmentEndcapXBlock'
        )

    def resource_string(self, path):  # pylint:disable=no-self-use
        """
        Handy helper for getting resources from our kit.
        """
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def create_fragment(self, html, context=None, css=None, javascript=None, initialize=None):
        """
        Create an XBlock, given an HTML resource string and an optional context, list of CSS
        resource strings, list of JavaScript resource strings, and initialization function name.
        """
        html = Template(self.resource_string(html))
        context = context or {}
        css = css or [self.CSS_FILE]
        javascript = javascript or []
        frag = Fragment(html.render(Context(context)))
        for sheet in css:
            frag.add_css(self.resource_string(sheet))
        for script in javascript:
            frag.add_javascript(self.resource_string(script))
        if initialize:
            frag.initialize_js(initialize)
        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):

        graded_target_id = data.get('graded_target_id')  # We cannot validate this ourselves
        if not graded_target_id:
            graded_target_id = None  # Avoid trying to set to an empty string - won't work
        self.graded_target_id = graded_target_id
        return {}

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("Assessment Endcap",
            """
            <vertical_demo>
                <assessmentendcap maxwidth="800" />
                <html_demo><div>Rate the video:</div></html_demo>
                <thumbs />
            </vertical_demo>
            """)
        ]
