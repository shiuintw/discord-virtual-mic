import argparse
import sys
from pathlib import Path


def patch_torch_load_for_fairseq():
    import torch

    original_load = torch.load

    def compatible_load(*args, **kwargs):
        kwargs.setdefault("weights_only", False)
        return original_load(*args, **kwargs)

    torch.load = compatible_load


def parse_args():
    parser = argparse.ArgumentParser(description="Run RVC voice conversion.")
    parser.add_argument("--input", required=True, help="Input wav path.")
    parser.add_argument("--output", required=True, help="Output wav path.")
    parser.add_argument("--model", required=True, help="RVC .pth model path.")
    parser.add_argument("--index", default="", help="Optional RVC .index path.")
    parser.add_argument("--device", default="cpu:0", help="RVC device, e.g. cpu:0 or cuda:0.")
    parser.add_argument("--version", default="v2", choices=["v1", "v2"], help="RVC model version.")
    parser.add_argument("--pitch", type=int, default=0, help="Transpose in semitones.")
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    model_path = Path(args.model)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    if not model_path.exists():
        raise FileNotFoundError(f"Model file does not exist: {model_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    patch_torch_load_for_fairseq()

    from rvc_python.infer import RVCInference

    rvc = RVCInference(device=args.device, version=args.version)
    rvc.load_model(str(model_path), version=args.version, index_path=args.index)
    rvc.set_params(f0up_key=args.pitch)
    rvc.infer_file(str(input_path), str(output_path))

    if not output_path.exists():
        raise RuntimeError(f"RVC did not create output file: {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"RVC inference failed: {exc}", file=sys.stderr)
        raise
