-- Shared handlers for the 2Do Alfred workflow's Script Filter scripts.
-- Loaded via `run script` (compiles plain-text source on the fly, so
-- this file can stay editable text -- no compiled .scpt, no install step).
script Lib
	on escapeJSON(txt)
		set txt to my replaceText(txt, "\\", "\\\\")
		set txt to my replaceText(txt, "\"", "\\\"")
		set txt to my replaceText(txt, return, " ")
		set txt to my replaceText(txt, linefeed, " ")
		return txt
	end escapeJSON

	on replaceText(sourceText, findText, replaceText)
		set AppleScript's text item delimiters to findText
		set theItems to text items of sourceText
		set AppleScript's text item delimiters to replaceText
		set newText to theItems as text
		set AppleScript's text item delimiters to ""
		return newText
	end replaceText

	-- 2Do's automation bridge wraps each list element in extra singleton
	-- lists (record -> {record} -> {{record}}); peel down to the record
	on unwrapRecord(x)
		repeat while (class of x is list) and (count of x) is 1
			set x to item 1 of x
		end repeat
		return x
	end unwrapRecord

	on taskToJSON(aTask, titlePrefix)
		set aTask to my unwrapRecord(aTask)
		set taskId to my escapeJSON(task_id of aTask)
		set taskTitle to my escapeJSON(titlePrefix & (title of aTask))
		set listTitle to my escapeJSON(list_title of aTask)

		set tagTitles to {}
		repeat with aTag in (tags of aTask)
			set aTag to my unwrapRecord(aTag)
			set end of tagTitles to (title of aTag)
		end repeat
		set AppleScript's text item delimiters to ", "
		set tagsJoined to tagTitles as text
		set AppleScript's text item delimiters to ""
		set tagsJoined to my escapeJSON(tagsJoined)

		try
			set dueDate to (due_date of aTask) as text
		on error
			set dueDate to ""
		end try

		try
			set theNotes to (notes of aTask) as text
			set theNotes to my escapeJSON(theNotes)
			if (length of theNotes) > 50 then set theNotes to (text 1 thru 50 of theNotes) & "…"
		on error
			set theNotes to ""
		end try

		set theSubtitle to "📁 " & listTitle
		if dueDate is not "" then set theSubtitle to theSubtitle & "  📅 " & dueDate
		if tagsJoined is not "" then set theSubtitle to theSubtitle & "  🏷️ " & tagsJoined
		if theNotes is not "" then set theSubtitle to theSubtitle & "  📝 " & theNotes

		return "{\"uid\":\"" & taskId & "\",\"title\":\"" & taskTitle & "\",\"subtitle\":\"" & theSubtitle & "\",\"arg\":\"" & taskId & "\"}"
	end taskToJSON

	on tasksToItemsJSON(theTasks, titlePrefix)
		set jsonItems to {}
		repeat with aTask in theTasks
			set end of jsonItems to my taskToJSON(aTask, titlePrefix)
		end repeat
		set AppleScript's text item delimiters to ","
		set itemsJoined to jsonItems as text
		set AppleScript's text item delimiters to ""
		return "{\"items\":[" & itemsJoined & "]}"
	end tasksToItemsJSON

	on emptyItemsJSON()
		return "{\"items\":[]}"
	end emptyItemsJSON
end script

return Lib
