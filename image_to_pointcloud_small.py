import argparse
import json
from pathlib import Path
import re
import numpy as np
from PIL import Image
from skimage import feature, morphology,transform


def image_to_pointcloud(
    img_array: np.ndarray,
    threshold: int = 127,
    canny_sigma: float = 1.0,
    thin_edges: bool = True,
    new_size:int=50
) -> np.ndarray:
    """
    Convert a grayscale image into an Nx2 point cloud using Canny edges.
    Each point represents the (x, y) coordinate of an edge pixel.
    """
    mask = img_array < threshold

    #edges = feature.canny(mask.astype(float), sigma=canny_sigma)
    dimension = (new_size, new_size)
    resized_image = transform.resize(mask, dimension)
    edges=resized_image
    if thin_edges:
        edges = morphology.thin(edges)
    
    y, x = np.nonzero(edges)
    return np.column_stack((x, y))


def save_pointcloud(
    points: np.ndarray,
    output_path: Path,
    label: str,
    source_set: str,
    image_name: str,
    image_shape: tupple,
) -> None:
    """
    Save a point cloud to a JSON file.
    """
    data = {
        "class": label,
        "source_set": source_set,
        "image": image_name,
        "width": image_shape[1],
        "height": image_shape[0],
        "num_points": len(points),
        "points": str(points.tolist()).replace('[', '(').replace(']', ')'),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w") as f:
        json.dump(data, f, indent=2)


def pair_label(image_number: int) -> str:
    """
    Assign one label to every two images in a set: 1/2 -> C1, 3/4 -> C2, etc.
    """
    pair_index = (image_number - 1) // 2
    return "C"+str(pair_index+1)


def process_dataset(
    input_dir: str,
    output_dir: str,
    threshold: int,
    canny_sigma: float,
    thin_edges: bool,
    new_size:int
) -> None:
    """
    Convert every PNG image in the dataset into a point cloud.
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    total_images = 0
    class_dirs = sorted(
        [d for d in input_dir.iterdir() if d.is_dir()],
        key=lambda p: int(p.name),
    )

    for class_dir in class_dirs:
        source_set = class_dir.name

        images = sorted(
            class_dir.glob("*.png"),
            key=lambda p: int(re.findall(r'\d+', p.stem)[0]),
        )

        print(f"Processing set {source_set}: {len(images)} images")

        for img_path in images:
            img_array = np.array(Image.open(img_path).convert("L"))
            label = pair_label(int(re.findall(r'\d+', img_path.stem)[0]))

            points = image_to_pointcloud(
                img_array,
                threshold=threshold,
                canny_sigma=canny_sigma,
                thin_edges=thin_edges,
                new_size=new_size
            )

            output_path = output_dir / source_set / f"{img_path.stem}.json"

            save_pointcloud(
                points=points,
                output_path=output_path,
                label=label,
                source_set=source_set,
                image_name=img_path.name,
                image_shape=(new_size,new_size),
            )

            total_images += 1

    print(f"\nFinished. Converted {total_images} images.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert PMF_OMNIGLOT images into point clouds."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the train dataset directory.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Directory where JSON point clouds will be saved.",
    )

    parser.add_argument(
        "--threshold",
        type=int,
        default=127,
        help="Pixel threshold used for binarization (default: 127).",
    )

    parser.add_argument(
        "--canny-sigma",
        type=float,
        default=1.0,
        help="Gaussian sigma used by the Canny filter (default: 1.0).",
    )

    parser.add_argument(
        "--thin",
        type=bool,
        default=True,
        help=" thinning .",
    )
    parser.add_argument(
        "--resize",
        type=int,
        default=50,
        help="Dimention for resizing",
    )

    args = parser.parse_args()

    process_dataset(
        input_dir=args.input,
        output_dir=args.output,
        threshold=args.threshold,
        canny_sigma=args.canny_sigma,
        thin_edges=args.thin,
        new_size=args.resize
    )


if __name__ == "__main__":
    main()