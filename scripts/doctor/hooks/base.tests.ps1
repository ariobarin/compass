Test-PortableGuardSilent -Name "unknown event" -Payload @{
    hook_event_name = "UnknownEvent"
}

Test-PortableGuardLauncherSilent -Name "unknown event" -Payload @{
    hook_event_name = "UnknownEvent"
}
