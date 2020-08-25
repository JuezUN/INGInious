import React from "react";
import {FormControl} from 'react-bootstrap';
import Task from './task';
import CustomAlert from './custom_alert';
import UltimatePagination from './ultimate_pagination';

class TaskList extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            query: '',
            timer: 0,
        };

        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e) {
        const newStateQuery = e.target.value;
        const updateFilteredTasks = this.props.callbackUpdateFilteredTasks;

        clearTimeout(this.state.timer);
        if (newStateQuery === "") {
            this.props.callbackUpdateTasks();
            this.setState({
                query: newStateQuery,
                timer: 0
            });
        } else {
            this.setState({
                query: newStateQuery,
                timer: setTimeout(() => updateFilteredTasks(newStateQuery), 500)
            });
        }
    };

    onChangePage = (page) => {
        console.log(this.state.query);
        if (this.state.query === "") {
            this.props.callbackUpdateTasks(page);
        } else {
            this.props.callbackUpdateFilteredTasks(this.state.query, page);
        }
    };

    addTaskToCourse = (courseId, taskId, bankId) => {
        this.props.callBackAddTaskToCourse(courseId, taskId, bankId, this.state.query);
    };

    getListOfTasks = () => {
        let tasks = this.props.tasks.map((task, i) => {
            return (<Task
                task_info={task}
                key={i}
                courses={this.props.courses}
                callBackAddTaskToCourse={this.addTaskToCourse}
            />)
        });

        if (!tasks.length) {
            tasks = "There are no tasks available.";
        }
        return tasks
    };

    render() {

        return (
            <div>
                <CustomAlert message={this.props.dataAlert.data.message}
                             isVisible={this.props.dataAlert.isVisibleAlert}
                             callbackParent={this.props.callbackOnChildChangedClose}
                             styleAlert={this.props.dataAlert.styleAlert}
                             titleAlert={this.props.dataAlert.titleAlert}
                             callbackSetAlertInvisible={this.props.callbackSetAlertInvisible}
                />

                <form className="custom-search-input">
                    <h5>Search tasks:</h5>
                    <FormControl
                        type="text"
                        value={this.props.query}
                        placeholder="Type a course id or name, task name or a tag"
                        onChange={this.handleChange}
                    />
                </form>

                <div>The following tasks are available for copying:</div>

                <div className="list-group">{this.getListOfTasks()}</div>

                <UltimatePagination
                    currentPage={this.props.page}
                    totalPages={this.props.totalPages}
                    onChange={this.onChangePage}
                />

            </div>
        );
    }
}

export default TaskList;