# Visual assets

The Franka FR3 robot visual meshes are from Google DeepMind's MuJoCo Menagerie:
https://github.com/google-deepmind/mujoco_menagerie/tree/main/franka_fr3

The accompanying Franka asset license is included at `static/licenses/FR3-LICENSE.txt`.
The original visual meshes are downloaded into `.build/franka_fr3/assets/` for rendering;
they are not included in the static website bundle. The video credits identify this source.

The visualization uses the study's kinematic transforms, adds original primitive geometry
for the gripper and grasped box, and replays the captured joint positions. Lighting, floor,
force arrows, snapshot plots, labels and composition are project visualization additions.
The rendered box geometry is unavailable to the estimator.

The website's structure is inspired by the RCI Lab SAPC project page:
https://rcilab.khu.ac.kr/sapc/

The layout, APCL icon, scripts, diagrams, captions and simulation videos were created
for this project. No SAPC video, image, or stylesheet is embedded.
