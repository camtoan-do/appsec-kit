# Dockerfile policy. Run: conftest test Dockerfile --policy policy/
package main

import rego.v1

from_images := [cmd.Value[0] | some cmd in input; cmd.Cmd == "from"]

deny contains msg if {
	not any_user
	msg := "Container must not run as root: add a USER instruction"
}

any_user if {
	some cmd in input
	cmd.Cmd == "user"
}

deny contains msg if {
	some img in from_images
	endswith(img, ":latest")
	msg := sprintf("Pin base image to a version or digest, not :latest (%s)", [img])
}

deny contains msg if {
	some img in from_images
	not contains(img, "slim")
	not contains(img, "distroless")
	not contains(img, "chainguard")
	msg := sprintf("Use a minimal base image (slim/distroless/chainguard), got %s", [img])
}

warn contains msg if {
	not any_healthcheck
	msg := "No HEALTHCHECK instruction"
}

any_healthcheck if {
	some cmd in input
	cmd.Cmd == "healthcheck"
}
