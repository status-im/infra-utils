# Script for renaming resources when redactoring from count to for_each.
# WARNING: Use '-no-color' flag when running 'terraform plan'.
/will be/{
    if ($5 == "updated") {
        next
    }
    if ($5 == "destroyed") {
        if ($2 ~ /host$/) { old = $2"[0]" }
        else { old = $2 }
        next
    }
    if ($5 == "created") {
        new = $2
    }
    printf "terraform state mv '%s' '%s'\n", old, new
}
