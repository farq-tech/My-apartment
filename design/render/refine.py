"""Photoreal refinement of Blender base renders with FLUX.1 Kontext [dev] via HF Inference Providers (fal-ai).
fal returns the image inline (sync_mode) because fal.media downloads are blocked by this environment's proxy.
usage: python3 refine.py IN.jpg OUT.jpg "prompt" [seed]
"""
import base64, os, sys
import huggingface_hub.inference._providers.fal_ai as fal
from huggingface_hub import InferenceClient

_orig = fal.get_session


class _S:
    def __init__(self, s):
        self.s = s

    def get(self, url, *a, **k):
        if isinstance(url, str) and url.startswith('data:'):
            class R:
                content = base64.b64decode(url.split(',', 1)[1])
            return R()
        return self.s.get(url, *a, **k)


fal.get_session = lambda: _S(_orig())

if __name__ == '__main__':
    src, dst, prompt = sys.argv[1:4]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    c = InferenceClient(provider='fal-ai', api_key=os.environ['HF_token'])
    img = c.image_to_image(open(src, 'rb').read(), prompt=prompt, model='black-forest-labs/FLUX.1-Kontext-dev',
                           guidance_scale=2.5, num_inference_steps=28, seed=seed, sync_mode=True)
    img.save(dst, quality=92)
    print('ok', dst, img.size)
