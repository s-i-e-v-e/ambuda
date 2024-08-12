import logging
from pathlib import Path
from slugify import slugify

from flask import flash, render_template
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import FileField, RadioField, StringField
from wtforms.validators import DataRequired, ValidationError
from wtforms.widgets import TextArea

from ambuda.views.proofing.decorators import p2_required
from ambuda.std import executor, kvs


def _is_allowed_document_file(filename: str) -> bool:
    """True iff we accept this type of document upload."""
    return Path(filename).suffix == ".pdf"


def _required_if_archive(message: str):
    def fn(form, field):
        source = form.pdf_source.data
        if source == "archive.org" and not field.data:
            raise ValidationError(message)

    return fn


def _required_if_local(message: str):
    def fn(form, field):
        source = form.pdf_source.data
        if source == "local" and not field.data:
            raise ValidationError(message)

    return fn


class CreateProjectForm(FlaskForm):
    pdf_source = RadioField(
        "Source",
        choices=[
            ("archive.org", "From archive.org"),
            ("local", "From my computer"),
        ],
        validators=[DataRequired()],
    )
    archive_identifier = StringField(
        "archive.org identifier",
        validators=[
            _required_if_archive("Please provide a valid archive.org identifier.")
        ],
    )
    local_file = FileField(
        "PDF file", validators=[_required_if_local("Please provide a PDF file.")]
    )
    local_title = StringField(
        "Title of the book (you can change this later)",
        validators=[
            _required_if_local(
                "Please provide a title for your PDF.",
            )
        ],
    )

    license = RadioField(
        "License",
        choices=[
            ("public", "Public domain"),
            ("copyrighted", "Copyrighted"),
            ("other", "Other"),
        ],
        validators=[DataRequired()],
    )
    custom_license = StringField(
        "License",
        widget=TextArea(),
        render_kw={
            "placeholder": "Please tell us about this book's license.",
        },
    )


@p2_required
def create_project():
    import ambuda.repo.project
    import ambuda.ocr.do_image_extraction
    from unstd import os
    import unstd.config
    form = CreateProjectForm()
    if form.validate_on_submit():
        title = form.local_title.data

        # TODO: add timestamp to slug for extra uniqueness?
        slug = slugify(title)

        # We accept only PDFs, so validate that the user hasn't uploaded some
        # other kind of document format.
        filename = form.local_file.raw_data[0].filename
        if not _is_allowed_document_file(filename):
            flash("Please upload a PDF.")
            return render_template("proofing/create-project.html", form=form)

        # Create all directories for this project ahead of time.
        # FIXME(arun): push this further into the Celery task.
        project_dir = Path(unstd.config.current.FLASK_UPLOAD_DIR) / "projects" / slug
        pdf_dir = project_dir / "pdf"
        page_image_dir = project_dir / "pages"
        os.make_dir(pdf_dir.__str__())
        os.make_dir(page_image_dir.__str__())

        # Save the original PDF so that it can be downloaded later or reused
        # for future tasks (thumbnails, better image formats, etc.)
        pdf_path = pdf_dir / "source.pdf"
        form.local_file.data.save(pdf_path)

        # get page count
        num_pages = ambuda.ocr.do_image_extraction.get_page_count(pdf_path.__str__())

        # add project to database
        logging.info(f'Received upload task "{title}" for path {pdf_path}.')
        ambuda.repo.project.add(
            display_title=title,
            creator_id=current_user.id,
            num_pages=num_pages
        )

        # start splitting pdf into images
        task_id = ambuda.ocr.do_image_extraction.split_pdf_into_pages(pdf_path, page_image_dir)
        kvs.set(f"{task_id}.slug", slug)
        ts = executor.ts_get(task_id)
        return render_template(
            "proofing/create-project-post.html",
            status=ts.status,
            current=ts.current,
            total=ts.total,
            percent=ts.percentage,
            task_id=ts.id,
        )

    return render_template("proofing/create-project.html", form=form)


def create_project_status(task_id):
    """AJAX summary of the task."""
    ts = executor.ts_get(task_id)
    slug = kvs.get(f"{task_id}.slug")
    executor.status()
    return render_template(
        "include/task-progress.html",
        status=ts.status,
        current=ts.current,
        total=ts.total,
        percent=ts.percentage,
        slug=slug,
    )
