import vtk
import numpy as np
from pathlib import Path

class CTBLVisualizer:
    def __init__(self):
        """
        Initialize the CTBL visualization system with VTK components.
        We'll load a volume dataset and apply a lookup table from a .ctbl file.
        """
        self.volume_mapper = vtk.vtkSmartVolumeMapper()
        self.volume_property = vtk.vtkVolumeProperty()
        self.volume = vtk.vtkVolume()

        self.renderer = vtk.vtkRenderer()
        self.render_window = vtk.vtkRenderWindow()
        self.interactor = vtk.vtkRenderWindowInteractor()

        # Initialize the pipeline
        self._setup_pipeline()

    def _setup_pipeline(self):
        """
        Set up the visualization pipeline with render window, interactor, and volume properties.
        """
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetSize(1024, 768)

        self.interactor.SetRenderWindow(self.render_window)
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(style)

        self.volume_property.SetInterpolationTypeToLinear()
        self.volume_property.ShadeOn()
        self.volume_property.SetAmbient(0.3)
        self.volume_property.SetDiffuse(0.7)
        self.volume_property.SetSpecular(0.2)

        self.volume.SetMapper(self.volume_mapper)
        self.volume.SetProperty(self.volume_property)

    def load_volume(self, volume_file_path):
        """
        Load a volumetric dataset for visualization.

        Args:
            volume_file_path (str): Path to the volume dataset (e.g., .nrrd or .mhd).
        """
        if not Path(volume_file_path).exists():
            raise FileNotFoundError(f"Volume file not found: {volume_file_path}")

        # Use a generic reader (replace with a specific reader if needed)
        reader = vtk.vtkNrrdReader()  # Replace with vtkMetaImageReader() for .mhd files
        reader.SetFileName(volume_file_path)
        reader.Update()

        self.volume_mapper.SetInputConnection(reader.GetOutputPort())

        # Print data information for verification
        print(f"Loaded volume file: {volume_file_path}")
        print(f"Dimensions: {reader.GetOutput().GetDimensions()}")
        print(f"Scalar range: {reader.GetOutput().GetScalarRange()}")

    def apply_ctbl(self, ctbl_file_path):
        """
        Apply a lookup table from a .ctbl file to the volume rendering.

        Args:
            ctbl_file_path (str): Path to the .ctbl file.
        """
        if not Path(ctbl_file_path).exists():
            raise FileNotFoundError(f"CTBL file not found: {ctbl_file_path}")

        # Initialize the lookup table
        lookup_table = vtk.vtkLookupTable()
        lookup_table.SetNumberOfTableValues(256)  # Default table size, can be adjusted
        lookup_table.Build()

        with open(ctbl_file_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            # Skip empty lines and comments
            if not line.strip() or line.startswith('#'):
                continue

            # Split the line and try to parse the numerical fields
            values = line.split()
            if len(values) >= 4:
                try:
                    # Extract index and RGB values
                    index = int(values[0])
                    r, g, b = [float(v) / 255.0 for v in values[1:4]]
                    lookup_table.SetTableValue(index, r, g, b, 1.0)  # Add as RGBA
                except ValueError:
                    print(f"Skipping invalid line in .ctbl: {line.strip()}")
                    continue

        # Convert the lookup table to a color transfer function
        color_transfer_function = vtk.vtkColorTransferFunction()
        for i in range(lookup_table.GetNumberOfTableValues()):
            rgba = lookup_table.GetTableValue(i)
            color_transfer_function.AddRGBPoint(i, rgba[0], rgba[1], rgba[2])

        # Apply the color transfer function to the volume
        self.volume_property.SetColor(color_transfer_function)

    def start(self):
        """
        Start the visualization and interaction loop.
        """
        if not self.renderer.HasViewProp(self.volume):
            self.renderer.AddVolume(self.volume)

        self.renderer.ResetCamera()
        self.render_window.Render()
        self.interactor.Start()

def main():
    """
    Main function demonstrating the use of CTBLVisualizer.
    """
    visualizer = CTBLVisualizer()

    try:
        # Replace with your volume and .ctbl file paths
        volume_file = r"c:\Users\PC\Desktop\vtk projekt\liver-2014-02-20\volumes\labels\combined.nrrd"
        ctbl_file = r"c:\Users\PC\Desktop\vtk projekt\liver-2014-02-20\misc\liver-segments.ctbl"

        # Load the volume dataset
        visualizer.load_volume(volume_file)

        # Apply the .ctbl lookup table
        visualizer.apply_ctbl(ctbl_file)

        # Start the visualization
        visualizer.start()

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
