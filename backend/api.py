from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, Response
from .extractors import extract_text
from .services import summarize_document, generate_stream, build_markdown_summary
from .models import DocumentSummary

router = APIRouter()


@router.post("/summarize", response_model=DocumentSummary)
async def summarize(file: UploadFile = File(...)):
    contents = await file.read()

    try:
        text = extract_text(contents, file.content_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        result = summarize_document(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result

@router.post("/summarize/stream")
async def summarize_stream(file: UploadFile = File(...)):
    contents = await file.read()

    try:
        text = extract_text(contents, file.content_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    system_prompt = "You are an expert at summarizing documents clearly and concisely."
    user_prompt = f"Provide a clear, well-organized summary of the following document:\n\n{text}"

    return StreamingResponse(generate_stream(system_prompt, user_prompt), media_type="text/plain")

from fastapi.responses import Response

@router.post("/summarize/download")
async def summarize_download(file: UploadFile = File(...)):
    contents = await file.read()

    try:
        text = extract_text(contents, file.content_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        result = summarize_document(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    markdown_content = build_markdown_summary(result)

    return Response(
        content=markdown_content,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=summary.md"}
    )