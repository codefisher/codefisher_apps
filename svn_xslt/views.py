from django.shortcuts import render

def xslt(request):
    return render(request, "svn_xslt/style.html", content_type="text/xsl")