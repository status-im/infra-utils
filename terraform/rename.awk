# Script for renaming Terraform resources when changing names.
# WARNING: Use '-no-color' flag when running 'terraform plan'.
BEGIN{
    old = new = ""
}
/will be/{
    resource = $2
    if (resource ~ "cloudflare_record") {
        next
    }
    if ($5 == "updated") {
        next
    }
    if ($5 == "destroyed") {
        old = resource
        if (new == "") {
            next
        }
    }
    if ($5 == "created") {
        new = resource
        if (new == "") {
            next
        }
    }
    if (old != "" && new != "") {
        printf "terraform state mv '%s' '%s'\n", old, new
    }
    old = new = ""
}
