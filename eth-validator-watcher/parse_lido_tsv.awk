{
    # Create a unique key for each value in the first column
    key = $1;
    clusters[key] = clusters[key] ",{\"public_key\":\"0x" $2 "\",\"labels\":[\"lido\",\"" key "\",\"Validator Client\"]}";
}
END {
    for (key in clusters) {
        # Create a JSON array for each key
        json_content = "[\n" clusters[key] "\n]";
        # Replace commas between objects with commas and newlines for pretty printing
        gsub(/},{/, "},\n{", json_content);
        # Write to a file named after the key
        filename = "lido-" key ".json";
        print json_content > filename;
        close(filename);
    }
}
