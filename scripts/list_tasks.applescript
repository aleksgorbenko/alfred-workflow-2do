-- Alfred Script Filter: searches 2Do tasks server-side as the user types
-- Alfred passes typed query as {query}; disable "Alfred filters results"
-- on this node, since 2Do's own search (title+notes+tags+locations) runs
-- per keystroke and is broader than local title-only matching
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

	if theQuery is "" then return lib's emptyItemsJSON()

	tell application "2Do"
		set theResult to query_tasks given arguments:{focus:"all", search:theQuery, include_completed:false, limit:30}
	end tell

	return lib's tasksToItemsJSON(tasks of theResult, "task")
end run
