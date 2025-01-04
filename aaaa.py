import vtk
from pathlib import Path
import zipfile
import os

def extract_files(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def load_nrrd_file(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"NRRD file not found: {file_path}")

    reader = vtk.vtkNrrdReader()
    reader.SetFileName(str(file_path))
    reader.Update()
    return reader, reader.GetOutput()

def create_volume_actor(reader):
    volume_mapper = vtk.vtkSmartVolumeMapper()
    volume_mapper.SetInputConnection(reader.GetOutputPort())

    # Create an opacity transfer function
    opacity_function = vtk.vtkPiecewiseFunction()
    opacity_function.AddPoint(45, 0.0)    # Background
    opacity_function.AddPoint(150, 0.1)   # Bones (adjust as needed)
    opacity_function.AddPoint(190, 0.9)  # Liver (start of liver intensity range)
    opacity_function.AddPoint(50, 0.7)  # Liver (end of liver intensity range)
    opacity_function.AddPoint(150, 0.0)  # Bones and high intensity values

    # Create a color transfer function
    color_function = vtk.vtkColorTransferFunction()
    color_function.AddRGBPoint(0, 0.0, 0.0, 0.0)    # Background (black)
    color_function.AddRGBPoint(100, 1.0, 0.5, 0.3)  # Liver (brownish)
    color_function.AddRGBPoint(150, 1.0, 0.7, 0.5)  # Liver (lighter brown)

    # Set the volume properties
    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetScalarOpacity(opacity_function)  # Use the opacity function
    volume_property.SetColor(color_function)           # Use the color function
    volume_property.ShadeOn()
    volume_property.SetInterpolationTypeToLinear()

    # Create a volume actor
    volume = vtk.vtkVolume()
    volume.SetMapper(volume_mapper)
    volume.SetProperty(volume_property)

    return volume



def add_slice_planes(volume_data, interactor):
    slice_planes = []
    for orientation in range(3):
        plane = vtk.vtkImagePlaneWidget()
        plane.SetInputData(volume_data)
        plane.SetPlaneOrientation(orientation)
        plane.SetInteractor(interactor)
        plane.SetSliceIndex(50)
        plane.DisplayTextOn()
        plane.SetKeyPressActivationValue('x')
        plane.On()

        slice_planes.append(plane)

    return slice_planes

def add_annotation(renderer):
    text_actor = vtk.vtkTextActor()
    text_actor.SetInput("Liver Visualization")
    text_actor.GetTextProperty().SetFontSize(24)
    text_actor.GetTextProperty().SetColor(1.0, 1.0, 1.0)
    text_actor.SetPosition(10, 10)

    renderer.AddActor2D(text_actor)

def customize_camera(renderer):
    camera = vtk.vtkCamera()
    camera.SetPosition(0, -500, -500)
    camera.SetFocalPoint(0, 0, 0)
    camera.SetViewUp(0, 0, 1)

    renderer.SetActiveCamera(camera)
    
def add_slice_planes_to_renderer(renderer, volume_data, interactor, orientation, slice_index):
    plane_widget = vtk.vtkImagePlaneWidget()
    plane_widget.SetInputData(volume_data)
    plane_widget.SetPlaneOrientation(orientation)  # 0: X, 1: Y, 2: Z
    plane_widget.SetSliceIndex(slice_index)
    plane_widget.SetInteractor(interactor)
    plane_widget.DisplayTextOn()
    plane_widget.SetKeyPressActivationValue('x')  # Optional key activation
    plane_widget.On()
    renderer.ResetCamera()

def create_colored_label_actor(label_data):
    # Create a lookup table for coloring
    lookup_table = vtk.vtkLookupTable()
    lookup_table.SetNumberOfTableValues(256)  # Adjust based on the number of labels
    lookup_table.SetRange(0, 255)  # Assuming label values are in the range [0, 255]
    lookup_table.Build()

    # Define colors for specific labels
    lookup_table.SetTableValue(0, 0.0, 0.0, 0.0, 0.0)  # Background (transparent)
    lookup_table.SetTableValue(1, 1.0, 0.0, 0.0, 1.0)  # Label 1: Red
    lookup_table.SetTableValue(2, 0.0, 1.0, 0.0, 1.0)  # Label 2: Green
    lookup_table.SetTableValue(3, 0.0, 0.0, 1.0, 1.0)  # Label 3: Blue
    # Add more labels as needed

    # Map label data to colors
    color_mapper = vtk.vtkImageMapToColors()
    color_mapper.SetInputData(label_data)
    color_mapper.SetLookupTable(lookup_table)
    color_mapper.Update()

    # Create a 2D image actor for the colored labels
    label_actor = vtk.vtkImageActor()
    label_actor.GetMapper().SetInputConnection(color_mapper.GetOutputPort())

    return label_actor

def load_label_file(label_file_path):
    if not label_file_path.exists():
        raise FileNotFoundError(f"Label file not found: {label_file_path}")

    reader = vtk.vtkNrrdReader()
    reader.SetFileName(str(label_file_path))
    reader.Update()
    return reader, reader.GetOutput()


    
def main():
    # Base directory for files
    base_dir = Path(r"C:\Users\julia\OneDrive\Pulpit\vtk projekt\liver-2014-02-20.zip")
    extract_to = base_dir.parent / "extracted"

    # Extract files
    if not extract_to.exists():
        extract_to.mkdir(parents=True, exist_ok=True)
        extract_files(base_dir, extract_to)

    # File paths
    volume_file = extract_to / 'liver-2014-02-20' / 'volumes' / 'grayscale' / 'IM-0001-0015.dcm.nrrd'
    label_file = extract_to / 'liver-2014-02-20' / 'volumes' / 'labels' / 'combined.nrrd'

    if not volume_file.exists() or not label_file.exists():
        print(f"Required files do not exist:\nVolume: {volume_file}\nLabels: {label_file}")
        return

    # Create renderer
    renderer = vtk.vtkRenderer()

    # Load and add volume to renderer
    volume_reader, volume_data = load_nrrd_file(volume_file)
    volume_actor = create_volume_actor(volume_reader)
    renderer.AddVolume(volume_actor)

    # Load and add label file to renderer
    label_reader, label_data = load_label_file(label_file)
    label_actor = create_colored_label_actor(label_data)
    renderer.AddActor(label_actor)

    # Background and annotation
    renderer.SetBackground(0.5, 0.3, 0.8)
    add_annotation(renderer)

    # Customize camera
    customize_camera(renderer)

    # Render window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Interactor
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    # Start visualization
    render_window.Render()
    render_window_interactor.Start()


if __name__ == "__main__":
    main()
