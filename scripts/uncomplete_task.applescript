-- Alfred Run Script action: marks chosen task as not completed in 2Do
-- Alfred passes selected task_id as {query}
on run argv
	set taskId to item 1 of argv

	tell application "2Do"
		uncomplete_task given arguments:{task_id:taskId}
	end tell
end run
