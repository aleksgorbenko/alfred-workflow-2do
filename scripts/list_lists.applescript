-- Alfred Script Filter: lists all 2Do lists + smart lists as JSON
use AppleScript version "2.4"
use scripting additions

set scriptDir to do shell script "dirname " & quoted form of (POSIX path of (path to me))
set lib to run script POSIX file (scriptDir & "/lib.applescript")

tell application "2Do"
	set listsResult to list_lists given arguments:{include_archived:false}
	set smartResult to list_smart_lists
end tell

set jsonItems to {}
repeat with aList in (lists of listsResult)
	set aList to lib's unwrapRecord(aList)
	set listId to lib's escapeJSON(list_id of aList)
	set listTitle to lib's escapeJSON(title of aList)
	set end of jsonItems to "{\"uid\":\"list-" & listId & "\",\"title\":\"📁 " & listTitle & "\",\"subtitle\":\"List\",\"arg\":\"list:" & listId & "\"}"
end repeat
repeat with aSmartList in (smart_lists of smartResult)
	set aSmartList to lib's unwrapRecord(aSmartList)
	set smartId to lib's escapeJSON(smart_list_id of aSmartList)
	set smartTitle to lib's escapeJSON(title of aSmartList)
	set end of jsonItems to "{\"uid\":\"smart-" & smartId & "\",\"title\":\"⚙️ " & smartTitle & "\",\"subtitle\":\"Smart List\",\"arg\":\"smart:" & smartId & "\"}"
end repeat

set AppleScript's text item delimiters to ","
set itemsJoined to jsonItems as text
set AppleScript's text item delimiters to ""

return "{\"items\":[" & itemsJoined & "]}"
