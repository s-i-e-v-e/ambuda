from ambuda.ocr import do_ocr
import logging
from flask import (
    flash,
    render_template,
    request,
)
from flask_babel import lazy_gettext as _l
from werkzeug.exceptions import abort
from ambuda import queries as q
from ambuda.views.proofing.decorators import p2_required
from ambuda.std import kvs
from ambuda.std import executor

LOG = logging.getLogger(__name__)


@p2_required
def batch_ocr(slug):
    project_ = q.project(slug)
    if project_ is None:
        abort(404)

    if request.method == "POST":
        task_id = do_ocr.run_ocr_for_project(project_)
        if not task_id:
            flash(_l("All pages in this project have at least one edit already."))
            return

        kvs.set(f"{task_id}.slug", slug)
        ts = executor.ts_get(task_id)
        return render_template(
            "proofing/projects/batch-ocr-post.html",
            project=project_,
            status=ts.status,
            current=ts.current,
            total=ts.total,
            percent=ts.percentage,
            task_id=ts.id,
        )

    return render_template(
        "proofing/projects/batch-ocr.html",
        project=project_,
    )


def batch_ocr_status(task_id):
    ts = executor.ts_get(task_id)
    slug = kvs.get(f"{task_id}.slug")
    executor.status()
    return render_template(
        "include/ocr-progress.html",
        status=ts.status,
        current=ts.current,
        total=ts.total,
        percent=ts.percentage,
        slug=slug,
    )

