import vtk
from pathlib import Path
import zipfile
import os

def extract_files(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def load_and_display_model(model_path):
    # Load the VTK model
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(str(model_path))
    reader.Update()

    # Create a mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor

def load_and_display_nrrd(file_path):
    # Load the NRRD file
    reader = vtk.vtkNrrdReader()
    reader.SetFileName(str(file_path))
    reader.Update()

    volume_mapper = vtk.vtkSmartVolumeMapper()
    volume_mapper.SetInputConnection(reader.GetOutputPort())

    # Create a volume
    volume = vtk.vtkVolume()
    volume.SetMapper(volume_mapper)

    return volume, reader.GetOutput()

def add_slice_planes(volume_data, interactor):

    slice_planes = []
    for orientation in range(3):
        # Create the plane
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

# def add_annotation(renderer):

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
    renderer.ResetCamera()

def main():
    # Base directory for files
    base_dir = Path(r"C:\Users\julia\OneDrive\Pulpit\vtk projekt\liver-2014-02-20.zip")
    extract_to = base_dir.parent / "extracted"

    # Extract files
    extract_files(base_dir, extract_to)

    # File paths
    #model_file = extract_to / 'liver-2014-02-20' / 'models' / 'Model_10_LiverSegment_III.vtk'
    volume_file = extract_to / 'liver-2014-02-20' / 'volumes' / 'grayscale' / 'IM-0001-0015.dcm.nrrd'
    #label_file = extract_to / 'liver-2014-02-20' / 'volumes' / 'labels' / 'combined.nrrd'

    # Debug: Print file paths
    #print(f"Model file: {model_file}")
    print(f"Volume file: {volume_file}")
    #print(f"Label file: {label_file}")

    # Check if files exist
    # if not model_file.exists():
        #print(f"Model file does not exist: {model_file}")
        #return 
    if not volume_file.exists():
        print(f"Volume file does not exist: {volume_file}")
        return
    #if not label_file.exists():
        print(f"Label file does not exist: {label_file}")
        return

    # Create renderer
    renderer = vtk.vtkRenderer()

    # Load and add model to renderer
    # model_actor = load_and_display_model(model_file)
    # renderer.AddActor(model_actor)

    # Load and add volume to renderer
    volume_actor, volume_data = load_and_display_nrrd(volume_file)
    renderer.AddVolume(volume_actor)

    renderer.SetBackground(0.5, 0.9, 0.7)  # Dark background

    #add_annotation(renderer)

    customize_camera(renderer)

    # Render window
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)

    # Interactor
    render_window_interactor = vtk.vtkRenderWindowInteractor()
    render_window_interactor.SetRenderWindow(render_window)

    slice_planes = add_slice_planes(volume_data, render_window_interactor)

    def toggle_slice_planes(obj, event):
        for plane in slice_planes:
            if plane.GetEnabled():
                plane.Off()
            else:
                plane.On()
        render_window.Render()
    
    render_window_interactor.AddObserver("KeyPressEvent", toggle_slice_planes)  

    # Start visualization
    render_window.Render()
    render_window_interactor.Start()

if __name__ == "__main__":
    main()