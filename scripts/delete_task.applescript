-- Alfred Run Script action: deletes chosen task in 2Do
-- Alfred passes selected task_id as {query}
on run argv
	set taskId to item 1 of argv

	tell application "2Do"
		delete_task given arguments:{task_id:taskId}
	end tell
end run
