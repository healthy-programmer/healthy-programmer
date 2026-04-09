# Utility functions for UI operations (Tkinter, etc.)

def animate_gif(label, frames, delay, frame_idx=0, anim_state=None):
    """
    Animate a GIF in a Tkinter label by cycling through its frames.
    """
    frame = frames[frame_idx]
    label.config(image=frame)
    label.image = frame
    next_idx = (frame_idx + 1) % len(frames)
    # Cancel previous animation if anim_state is provided
    if anim_state is not None:
        if anim_state["timer_id"]:
            label.after_cancel(anim_state["timer_id"])
        anim_state["timer_id"] = label.after(delay, animate_gif, label, frames, delay, next_idx, anim_state)
    else:
        label.after(delay, animate_gif, label, frames, delay, next_idx)