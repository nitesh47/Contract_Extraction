import argparse, asyncio, json
from pathlib import Path
from typing import Optional
from models.llm_client import LLMClient
from extractors.metadata_extractor import extract_metadata
from utils.async_utils import gather_with_concurrency

async def _proc(pdf:Path,client:LLMClient,*,save:bool,od:Optional[Path]):
    meta = await extract_metadata(pdf,client,save=save,output_dir=od)
    if not save:
        print(json.dumps(meta.model_dump(mode='json',exclude_none=True),indent=2))

async def main(dir_path:Path,concurrency:int,save:bool,output_dir:Optional[Path]):
    pdfs = [f for f in dir_path.rglob('*') if f.is_file() and f.suffix.lower() == '.pdf']
    print(pdfs)
    if not pdfs: raise SystemExit('No PDFs found')
    async with LLMClient() as client:
        await gather_with_concurrency(concurrency,*(_proc(p,client,save=save,od=output_dir) for p in pdfs))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description='Extract contract metadata')
    ap.add_argument('--directory',type=Path)
    ap.add_argument('-c','--concurrency',type=int,default=4)
    ap.add_argument('--output-dir',type=Path,default=None)
    ap.add_argument('--no-save',dest='save',action='store_false')
    args=ap.parse_args()
    try:
        asyncio.run(main(args.directory,args.concurrency,args.save,args.output_dir))
    except KeyboardInterrupt:
        print('Cancelled')
