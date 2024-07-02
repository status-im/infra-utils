# Script for renaming Terraform resources when changing names.
# WARNING: Use '-no-color' flag when running 'terraform plan'.
/will be/{
    if ($5 == "updated") {
        next
    }
    if ($5 == "destroyed") {
        old = $2
        next
    }
    if ($5 == "created") {
        new = $2
    }
    printf "terraform state mv '%s' '%s'\n", old, new
}
