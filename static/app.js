inputNewTask = document.querySelector('#new-task');
formNewTask = document.querySelector("#form-new-task");
taskList = document.querySelector('#task-list');

function addTask(taskName) {

    let response = get_request('/tasks', {
        method: "POST",
        headers: {
            'Content-type': 'application/json'
        },
        body: JSON.stringify({"name": taskName})
    });

    response.then(data => {
        if (data.status === "OK") {
            //new list item
            let new_li = document.createElement('li');

            //set attribute list id
            let task_id_attr = document.createAttribute('task_id');
            task_id_attr.value = data["id"];
            new_li.setAttributeNode(task_id_attr);

            // create inner elements of list item
            let html = `
            <span>${data["name"]}</span>
            <input type="checkbox" class="done-checkbox" id="${data["id"]}">
            <label for="${data["id"]}" class="checkbox-label">
                    <div>✔</div>
                </label>
                <button>x</button>`

            new_li.innerHTML = html;
            taskList.appendChild(new_li);
        }
    });
}

function taskListOnClick(e) {
    //DELETE
    if (e.target.tagName === 'BUTTON') {

        let li = e.target.closest('li');
        let task_id = li.getAttribute('task_id');
        let response = get_request('/tasks/' + task_id, {
            method: "DELETE"
        });

        response.then(data => {
            if (data["status"] === "OK") {
                taskList.removeChild(li);
            }
        });
    }

    // UPDATE - CHECKED
    if (e.target.tagName === 'INPUT') {
        if (e.target.getAttribute('type') === 'checkbox') {   //if it is a checkbox

            //get id and current state
            let li = e.target.closest('li');
            let task_id = li.getAttribute('task_id');
            let state = 0;
            if (e.target.checked) {
                state = 1;
            }

            let response = get_request('/tasks/' + task_id, {
                method: "PUT",
                headers: {
                    'Content-type': 'application/json'
                },
                body: JSON.stringify({"done": state})
            });

            response.then(data => {
                if (data["status"] === "OK") {
                    process_checked(e.target);
                } else {
                    e.target.checked = !e.target.checked;
                }
            });
        }
    }
}

//DECORATE CHECKED
function process_checked(checkbox) {
    if (checkbox.checked) {
        checkbox.closest('li').querySelector('span').style.textDecoration = '#C3C3C3 line-through';
        checkbox.closest('li').querySelector('span').style.color = '#C3C3C3';
    } else {
        checkbox.closest('li').querySelector('span').style.textDecoration = 'none';
        checkbox.closest('li').querySelector('span').style.color = 'black';
    }
}


async function get_request(url, params = {}) {
    let response = await fetch(url, params);
    return await response.json();
}

function set_checkboxes() {
    let checkboxes = taskList.querySelectorAll('input[type=checkbox]');
    checkboxes.forEach(checkbox =>{
        process_checked(checkbox);
    });
}

taskList.addEventListener('click', taskListOnClick);
formNewTask.addEventListener('submit', e => {
    e.preventDefault();
    if (inputNewTask.value !== "") {
        addTask(inputNewTask.value);
    }
    inputNewTask.value = "";
})

set_checkboxes()