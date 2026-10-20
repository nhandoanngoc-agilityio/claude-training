def test_delete_unknown_task_returns_404(client):
    """#11: deleting an ID that does not exist reported success."""
    response = client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_delete_twice_returns_404_the_second_time(client):
    task = client.post("/tasks", json={"title": "Temp"}).json()

    assert client.delete(f"/tasks/{task['id']}").status_code == 204
    assert client.delete(f"/tasks/{task['id']}").status_code == 404
    assert client.get(f"/tasks/{task['id']}").status_code == 404
