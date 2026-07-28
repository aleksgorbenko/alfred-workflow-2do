-- Alfred Script Filter: searches COMPLETED 2Do tasks server-side as the
-- user types, for undoing an accidental complete. Alfred passes typed
-- query as {query}; disable "Alfred filters results" on this node.
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
		set theResult to query_tasks given arguments:{focus:"done", search:theQuery, limit:30}
	end tell

	return lib's tasksToItemsJSON(tasks of theResult, "✅ ")
end run
