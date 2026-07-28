-- Alfred Script Filter: lists uncompleted tasks within a single list or
-- smart list (chosen previously), then narrows by search as user types.
-- Requires an "Arg and Vars" node upstream that sets workflow variable
-- "scope" to the selected list_lists.applescript arg ("list:ID" or
-- "smart:ID") and passes an empty string through as the next argument.
use AppleScript version "2.4"
use scripting additions

on run argv
	set scriptDir to do shell script "dirname " & quoted form of (POSIX path of (path to me))
	set lib to run script POSIX file (scriptDir & "/lib.applescript")

	if (count of argv) > 0 then
		set theQuery to item 1 of argv
	else
		set theQuery to ""
	end if

	set theScope to (system attribute "scope")
	set colonPos to offset of ":" in theScope
	set scopeType to text 1 thru (colonPos - 1) of theScope
	set scopeId to text (colonPos + 1) thru -1 of theScope

	if scopeType is "smart" then
		if theQuery is "" then
			tell application "2Do"
				set theResult to query_tasks given arguments:{smart_list_id:scopeId, include_completed:false, limit:50}
			end tell
		else
			tell application "2Do"
				set theResult to query_tasks given arguments:{smart_list_id:scopeId, search:theQuery, include_completed:false, limit:50}
			end tell
		end if
	else
		if theQuery is "" then
			tell application "2Do"
				set theResult to query_tasks given arguments:{list_id:scopeId, include_completed:false, limit:50}
			end tell
		else
			tell application "2Do"
				set theResult to query_tasks given arguments:{list_id:scopeId, search:theQuery, include_completed:false, limit:50}
			end tell
		end if
	end if

	return lib's tasksToItemsJSON(tasks of theResult, "")
end run
