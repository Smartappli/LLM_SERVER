from django import forms


class ModelDiscoveryForm(forms.Form):
    keywords = forms.CharField(
        initial="medical biomed biomedical clinical health",
        help_text="Space-separated keywords used for Hugging Face search.",
    )
    limit_per_keyword = forms.IntegerField(min_value=1, max_value=500, initial=100)
    output_dir = forms.CharField(initial="models")
    download = forms.BooleanField(required=False, initial=False)
    all_files = forms.BooleanField(required=False, initial=False)
    token = forms.CharField(required=False, widget=forms.PasswordInput(render_value=True))
