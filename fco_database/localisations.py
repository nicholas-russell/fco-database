def template_vars(request):
    return {
        "new_member": {
            "volunteer_text": "Select any volunteering you would be interested in by searching",
            "mailing_list_text": "Please tick if you <strong>do not</strong> want to be included in our \
                                mailing list. The Food Co-operative is reliant on volunteers to be able to \
                                give greater benefits back to our members and community. If you opt out of our \
                                mailing list, you’ll miss out on emails regarding volunteering opportunities.",
            "top_help_text": "<p>Explanation text on membership process here.</p>",
            "mid_help_text": "<p>Please select a membership type, then complete details below.</p>"
        }
    }
