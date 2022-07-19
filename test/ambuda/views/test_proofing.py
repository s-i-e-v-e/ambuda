def test_index(client):
    resp = client.get("/proofing/")
    assert ">Proofreading<" in resp.text


def test_upload__unauth(client):
    resp = client.get("/proofing/upload")
    assert resp.status_code == 302


def test_upload__auth(rama_client):
    resp = rama_client.get("/proofing/upload")
    assert resp.status_code == 200


def test_project(client):
    resp = client.get("/proofing/test-project/")
    assert resp.status_code == 200


def test_download_project(client):
    resp = client.get("/proofing/test-project/download")
    assert resp.status_code == 200


def test_edit_page(client):
    resp = client.get("/proofing/test-project/1/")
    assert resp.status_code == 200


def test_page_history(client):
    resp = client.get("/proofing/test-project/1/history")
    assert resp.status_code == 200
