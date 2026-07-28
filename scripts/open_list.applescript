-- Alfred Run Script action: opens chosen list or smart list in 2Do
-- Alfred passes selected arg as {query}, formatted "list:<id>" or "smart:<id>"
on run argv
	set theArg to item 1 of argv
	set colonPos to offset of ":" in theArg
	set theType to text 1 thru (colonPos - 1) of theArg
	set theId to text (colonPos + 1) thru -1 of theArg

	tell application "2Do"
		activate
		if theType is "smart" then
			select_smart_list given arguments:{smart_list_id:theId}
		else
			select_list given arguments:{list_id:theId}
		end if
	end tell
end run
