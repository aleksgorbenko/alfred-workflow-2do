-- Alfred Script Filter: lists today's (+ overdue) uncompleted 2Do tasks,
-- shown immediately on empty query, narrowed by search as user types.
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

	if theQuery is "" then
		tell application "2Do"
			set theResult to query_tasks given arguments:{focus:"today", include_completed:false, limit:50}
		end tell
	else
		tell application "2Do"
			set theResult to query_tasks given arguments:{focus:"today", search:theQuery, include_completed:false, limit:50}
		end tell
	end if

	return lib's tasksToItemsJSON(tasks of theResult, "")
end run
