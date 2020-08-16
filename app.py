import sys
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:01478520@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo: {self.id}, description: {self.description}>'


class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)

    def __repr__(self):
        return f'<Todo: {self.id}, description: {self.description}>'


@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html',
                           todos=Todo.query.filter_by(list_id=list_id).order_by('id').all(),
                           lists=TodoList.query.all(),
                           active_list=TodoList.query.get(list_id)
                           )


@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))


@app.route('/todos/create', methods=['POST'])
def create():
    json_data = request.get_json()
    description = json_data.get('description')
    list_id = json_data.get('list_id')
    if description is not None:
        db_description = description.strip()
        if db_description:
            error = False
            body = dict()
            try:
                todo = Todo(description=description, list_id=list_id)
                db.session.add(todo)
                db.session.commit()
                body['id'] = todo.id
                body['description'] = todo.description
                body['list_id'] = todo.list_id
            except:
                db.session.rollback()
                error = True
                print(sys.exc_info())
            finally:
                db.session.close()

            if not error:
                return jsonify({
                    'id': body.get('id'),
                    'description': body.get('description'),
                    'list_id': body.get('list_id')
                })
            else:
                return jsonify({
                    'success': False
                })

        else:
            return jsonify({
                'success': False
            })
    else:
        return jsonify({
            'success': False
        })


@app.route('/todos/delete', methods=['POST'])
def delete():
    json_data = request.get_json()
    todo_id = json_data.get('todo_id')
    if todo_id is not None:
        error = False
        try:
            todo = Todo.query.get(todo_id)

            # Todo.query.filter_by(id=todo_id).delete()
            db.session.delete(todo)
            db.session.commit()
        except:
            db.session.rollback()
            error = True
            print(sys.exc_info())
        finally:
            db.session.close()

        if not error:
            return jsonify({
                'id': todo_id,
                'success': True
            })
        else:
            return jsonify({
                'success': False
            })
    else:
        return jsonify({
            'success': False
        })


@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    json_data = request.get_json()
    completed = json_data.get('completed', False)

    if todo_id is not None:
        error = False
        try:
            todo = Todo.query.get(todo_id)

            if todo:
                todo.completed = completed
                db.session.commit()
            else:
                return jsonify({
                    'success': False
                })
        except:
            db.session.rollback()
            error = True
            print(sys.exc_info())
        finally:
            db.session.close()

        if not error:
            return jsonify({
                'success': True
            })
        else:
            return jsonify({
                'success': False
            })
    else:
        return jsonify({
            'success': False
        })


if __name__ == '__main__':
    app.run(debug=True, port=7000)
