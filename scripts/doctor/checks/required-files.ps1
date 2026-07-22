if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    $problems.Add("git is not on PATH")
}
else {
    # The required-file set is the git index: every tracked file must exist in
    # the working tree and no tracked file may live under local scratch. git is
    # the single source of truth for which files belong, so this check derives
    # from it directly instead of maintaining a second hand-written list.
    $trackedFiles = @(& git -C $repoRoot ls-files 2>$null)
    foreach ($trackedFile in $trackedFiles) {
        $trackedPath = Get-DoctorFullPath -Path (Join-Path $repoRoot $trackedFile)
        if (Test-LocalScratchPath -Path $trackedPath) {
            $problems.Add("tracked local scratch path: $trackedFile")
            continue
        }
        if (-not (Test-Path -LiteralPath $trackedPath)) {
            $problems.Add("tracked file missing from working tree: $trackedFile")
        }
    }
}
