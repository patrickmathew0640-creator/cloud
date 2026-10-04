# Preview render (not part of the Unity project)

`deliverables/virtual_shopping_complex_walkthrough.mp4` was rendered from these files. The cloud
machine that made it has no Unity editor, so the mall is rebuilt here in three.js, using the same
coordinates, sizes, colours, products, labels and UI layout as the C# scripts. The video shows what
the Unity scene is designed to look like; it was not recorded in Unity.

Unity is outside this folder (`Assets/` only), so these files have no effect on the Unity project.

To regenerate it:

```
npm i three@0.170.0 playwright
npx http-server -p 8099 .        # in this folder
node capture.mjs range 0 111 30 frames
ffmpeg -framerate 30 -i frames/f_%05d.jpg -c:v libx264 -crf 20 -pix_fmt yuv420p walkthrough.mp4
```
