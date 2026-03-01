import bpy
import os
import json

class REORDER_OT_apply_order(bpy.types.Operator):
    bl_idname = "reorder_npanel_tabs.apply_order"
    bl_label = "Apply Tab Order"

    def execute(self, context):
        scn = context.scene
        new_order = [item.name for item in scn.reorder_tab_list]
        scn['reorder_npanel_tab_order'] = new_order
        # Automatically save to file
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(addon_dir, "tab_order.json")
        with open(save_path, "w") as f:
            json.dump(new_order, f)
        panels = [cls for cls in bpy.types.Panel.__subclasses__()
                  if hasattr(cls, 'bl_space_type') and hasattr(cls, 'bl_region_type')
                  and cls.bl_space_type == 'VIEW_3D' and cls.bl_region_type == 'UI']
        for cls in panels:
            try:
                bpy.utils.unregister_class(cls)
            except Exception:
                pass
        for tab_name in new_order:
            for cls in panels:
                if getattr(cls, 'bl_category', '') == tab_name or getattr(cls, 'bl_category', '').startswith(tab_name):
                    setattr(cls, 'bl_category', tab_name)
                    try:
                        bpy.utils.register_class(cls)
                    except Exception:
                        pass
        self.report({'INFO'}, "Tab order applied and saved! (switch workspace or reload UI to see changes)")
        return {'FINISHED'}


class REORDER_OT_move_up(bpy.types.Operator):
    bl_idname = "reorder_npanel_tabs.move_up"
    bl_label = "Move Tab Up"

    def execute(self, context):
        scn = context.scene
        idx = scn.reorder_tab_index
        if idx > 0:
            scn.reorder_tab_list.move(idx, idx-1)
            scn.reorder_tab_index -= 1
        return {'FINISHED'}

class REORDER_OT_move_down(bpy.types.Operator):
    bl_idname = "reorder_npanel_tabs.move_down"
    bl_label = "Move Tab Down"

    def execute(self, context):
        scn = context.scene
        idx = scn.reorder_tab_index
        if idx < len(scn.reorder_tab_list)-1:
            scn.reorder_tab_list.move(idx, idx+1)
            scn.reorder_tab_index += 1
        return {'FINISHED'}

bl_info = {
    "name": "Simple N-Panel Organizer",
    "author": "OPQA Videogames",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar (N-Panel)",
    "description": "Organize, reorder, and resize your Blender N-Panel tabs easily. Tab order is persistent and automatically saved.",
    "category": "3D View"
}
from bpy.props import StringProperty



def get_npanel_tab_names():
    tabs = set()
    for cls in bpy.types.Panel.__subclasses__():
        if hasattr(cls, 'bl_space_type') and hasattr(cls, 'bl_region_type'):
            if cls.bl_space_type == 'VIEW_3D' and cls.bl_region_type == 'UI':
                tabs.add(getattr(cls, 'bl_category', ''))
    return sorted(tabs)

class REORDER_UL_panel_list(bpy.types.UIList):
    bl_idname = "REORDER_UL_panel_list"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=f"{item.name}")

class REORDER_OT_refresh_list(bpy.types.Operator):
    bl_idname = "reorder_npanel_tabs.refresh_list"
    bl_label = "Refresh Panel List"

    def execute(self, context):
        scn = context.scene
        scn.reorder_panel_list.clear()
        tabs = get_npanel_tab_names()
        for cls in panels:
            item = scn.reorder_panel_list.add()
            item.name = cls.__name__
            item.tab = getattr(cls, 'bl_category', '')
        self.report({'INFO'}, "Panel list refreshed!")
        return {'FINISHED'}

class REORDER_OT_refresh_tabs(bpy.types.Operator):
    bl_idname = "reorder_npanel_tabs.refresh_tabs"
    bl_label = "Refresh Tab List"

    def execute(self, context):
        scn = context.scene
        scn.reorder_tab_list.clear()
        tabs = get_npanel_tab_names()
        for tab in tabs:
            item = scn.reorder_tab_list.add()
            item.name = tab
        self.report({'INFO'}, "Tab list refreshed!")
        return {'FINISHED'}
class REORDER_PT_main_panel(bpy.types.Panel):
    bl_label = "Simple N-Panel Organizer"
    bl_idname = "REORDER_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ReOrder"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        layout.operator("reorder_npanel_tabs.refresh_tabs", text="Refresh Tabs")
        # Remove Save/Reset buttons above the list (do not add them here)
        layout.label(text="N-Panel Tabs (Headers):")
        # Add a resizable template_list for the tab list
        layout.template_list("REORDER_UL_panel_list", "", scn, "reorder_tab_list", scn, "reorder_tab_index", rows=10)
        row = layout.row()
        row.operator("reorder_npanel_tabs.move_up", text="Up")
        row.operator("reorder_npanel_tabs.move_down", text="Down")
        # Place the action buttons below the tab list and up/down buttons
        layout.separator()
        apply_row = layout.row()
        apply_row.operator("reorder_npanel_tabs.apply_order", text="Apply Tab Order")
class REORDER_OT_save_order(bpy.types.Operator):
    bl_idname = "reorder_npanel_tabs.save_order"
    bl_label = "Save Tab Order"

    def execute(self, context):
        scn = context.scene
        order = [item.name for item in scn.reorder_tab_list]
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(addon_dir, "tab_order.json")
        with open(save_path, "w") as f:
            json.dump(order, f)
        self.report({'INFO'}, f"Tab order saved to {save_path}")
        return {'FINISHED'}

    bl_label = "Apply Panel Order"

    def execute(self, context):
        scn = context.scene
        new_order = [item.name for item in scn.reorder_tab_list]
        # Save order to custom property
        scn['reorder_npanel_tab_order'] = new_order
        # Gather all panels
        panels = [cls for cls in bpy.types.Panel.__subclasses__()
                  if hasattr(cls, 'bl_space_type') and hasattr(cls, 'bl_region_type')
                  and cls.bl_space_type == 'VIEW_3D' and cls.bl_region_type == 'UI']
        # Unregister all panels
        for cls in panels:
            try:
                bpy.utils.unregister_class(cls)
            except Exception:
                pass
        # Set bl_category and register in new tab order
        for tab_name in new_order:
            for cls in panels:
                if getattr(cls, 'bl_category', '') == tab_name or getattr(cls, 'bl_category', '').startswith(tab_name):
                    setattr(cls, 'bl_category', tab_name)
                    try:
                        bpy.utils.register_class(cls)
                    except Exception:
                        pass
        self.report({'INFO'}, "Tab order applied! (switch workspace or reload UI to see changes)")
        return {'FINISHED'}



class ReorderTabItem(bpy.types.PropertyGroup):
    name: StringProperty()


def register():
    # Add workspace change handler to reapply tab order automatically
    def workspace_handler(dummy):
        scn = bpy.context.scene
        addon_dir = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(addon_dir, "tab_order.json")
        if scn and os.path.exists(save_path):
            with open(save_path, "r") as f:
                tabs = json.load(f)
            panels = [cls for cls in bpy.types.Panel.__subclasses__()
                      if hasattr(cls, 'bl_space_type') and hasattr(cls, 'bl_region_type')
                      and cls.bl_space_type == 'VIEW_3D' and cls.bl_region_type == 'UI']
            for cls in panels:
                try:
                    bpy.utils.unregister_class(cls)
                except Exception:
                    pass
            for tab_name in tabs:
                for cls in panels:
                    if getattr(cls, 'bl_category', '') == tab_name or getattr(cls, 'bl_category', '').startswith(tab_name):
                        setattr(cls, 'bl_category', tab_name)
                        try:
                            bpy.utils.register_class(cls)
                        except Exception:
                            pass
    bpy.app.handlers.depsgraph_update_post.append(workspace_handler)
    for cls in [ReorderTabItem, REORDER_UL_panel_list, REORDER_PT_main_panel, REORDER_OT_move_up, REORDER_OT_move_down, REORDER_OT_apply_order, REORDER_OT_refresh_tabs, REORDER_OT_save_order]:
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
        bpy.utils.register_class(cls)
    if not hasattr(bpy.types.Scene, "reorder_tab_list"):
        bpy.types.Scene.reorder_tab_list = bpy.props.CollectionProperty(type=ReorderTabItem)
    if not hasattr(bpy.types.Scene, "reorder_tab_index"):
        bpy.types.Scene.reorder_tab_index = bpy.props.IntProperty(default=0)
    # No load_post handler needed



def unregister():
    # Remove workspace change handler
    bpy.app.handlers.depsgraph_update_post[:] = [h for h in bpy.app.handlers.depsgraph_update_post if not getattr(h, '__name__', '') == 'workspace_handler']
    for cls in [ReorderTabItem, REORDER_UL_panel_list, REORDER_PT_main_panel, REORDER_OT_move_up, REORDER_OT_move_down, REORDER_OT_apply_order, REORDER_OT_refresh_tabs]:
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    if hasattr(bpy.types.Scene, "reorder_tab_list"):
        del bpy.types.Scene.reorder_tab_list
    if hasattr(bpy.types.Scene, "reorder_tab_index"):
        del bpy.types.Scene.reorder_tab_index

if __name__ == "__main__":
    register()
