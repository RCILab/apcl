# Visual assets

The Franka FR3 robot visual meshes are from Google DeepMind's MuJoCo Menagerie:
https://github.com/google-deepmind/mujoco_menagerie/tree/main/franka_fr3

The accompanying Franka asset license is included at `static/licenses/FR3-LICENSE.txt`.
The original visual meshes are downloaded into `.build/franka_fr3/assets/` for rendering;
they are not included in the static website bundle.

The visualization uses the study's kinematic transforms, adds original primitive geometry
for the gripper, grasped fixture, attachment eyelets and hanging weight, and replays two sets of captured joint positions.
Two copies of the robot are translated apart and shown with matching cameras, with contact estimates projected
from their actual tool-frame coordinates. Marker symbols are enlarged for visibility. Lighting, floor,
cable appearance, snapshot plots, labels and composition are project visualization additions.
The suspended weight is a simulated free rigid body, connected to the fixture by a unilateral
MuJoCo spatial-tendon length constraint. The fixture geometry is unavailable to the estimator.

The layout, APCL icon, scripts, diagrams, captions and simulation videos were created
for this project.
