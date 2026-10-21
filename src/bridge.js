function run(argv) {
  const app = Application("2Do");
  const call = (command, args) => app[command]({ arguments: args || {} });

  const parentOf = (() => {
    const known = {};
    return (taskId) => {
      if (!(taskId in known)) {
        try {
          const parent = call("get_task", { task_id: taskId }).task;
          known[taskId] = { task_id: parent.task_id, title: parent.title, task_type: parent.task_type };
        } catch (error) {
          known[taskId] = null;
        }
      }
      return known[taskId];
    };
  })();

  const withParents = (tasks) =>
    tasks.map((task) => (task.parent_task_id ? Object.assign(task, { parent: parentOf(task.parent_task_id) }) : task));

  const taskIndex = () => {
    const tasks = call("query_tasks", { focus: "all", include_completed: false }).tasks;
    const parents = tasks.filter((task) => task.child_task_ids && task.child_task_ids.length);
    const subtasks = parents.flatMap((parent) =>
      call("list_subtasks", { task_id: parent.task_id, include_completed: false }).tasks.map((task) =>
        Object.assign(task, { parent: { task_id: parent.task_id, title: parent.title, task_type: parent.task_type } }),
      ),
    );
    return tasks.concat(subtasks);
  };

  const perform = (request) => {
    switch (request.op) {
      case "tasks": {
        const result = call(request.command, request.arguments);
        return withParents(result.tasks || [result.task]);
      }
      case "task_index":
        return taskIndex();
      case "ui":
        app.activate();
        return call(request.command, request.arguments);
      default:
        return call(request.command, request.arguments);
    }
  };

  return JSON.stringify(
    JSON.parse(argv[0]).map((request) => {
      try {
        return { result: perform(request) };
      } catch (error) {
        return { error: String(error.message || error) };
      }
    }),
  );
}
