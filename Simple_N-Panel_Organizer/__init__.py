bl_info = {
    "name": "Simple N-Panel Organizer",
    "author": "OPQA Videogames",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar (N-Panel)",
    "description": "Organize, reorder, and resize N-panel tabs with persistence.",
    "category": "UI",
    "support": "COMMUNITY",
    "doc_url": "https://github.com/DarkHareVideoGames/Simple-N-Panel-Organizer/blob/main/MANUAL.md"
}

import bpy
import json
import os

class NPanelTabOrder(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()

class REORDER_UL_tab_order(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False)

class REORDER_PT_npanel_tabs(bpy.types.Panel):
    bl_label = "Simple N-Panel Organizer"
    bl_idname = "REORDER_PT_npanel_tabs"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Simple N-Panel Organizer'
    # bl_options removed so panel loads open by default

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        pass

    def draw(self, context):
        layout = self.layout
        layout.scale_x = 5  # Make panel much wider
        layout.scale_y = 10  # Make panel much taller
        wm = context.window_manager
        # Refresh button at the top
        layout.operator("reorder.refresh_tabs", text="Refresh Tabs")
        layout.label(text="Reorder your N-panel tabs below:")
        row = layout.row(align=True)
        # Tab list with selection
        row.template_list("REORDER_UL_tab_order", "", wm, "npanel_tab_order", wm, "npanel_tab_order_index")
        # Up/Down arrows next to the list for selected item
        col_arrows = row.column(align=True)
        col_arrows.operator("reorder.move_tab_up", text="", icon="TRIA_UP")
        col_arrows.operator("reorder.move_tab_down", text="", icon="TRIA_DOWN")
        # Apply Order button at the bottom
        layout.operator("reorder.apply_order", text="Apply Order & Save")

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        # Refresh button at the top
        layout.operator("reorder.refresh_tabs", text="Refresh Tabs")
        layout.label(text="Reorder your N-panel tabs below:")
        row = layout.row(align=True)
        # Tab list with selection
        row.template_list("REORDER_UL_tab_order", "", wm, "npanel_tab_order", wm, "npanel_tab_order_index")
        # Up/Down arrows next to the list for selected item
        col_arrows = row.column(align=True)
        col_arrows.operator("reorder.move_tab_up", text="", icon="TRIA_UP")
        col_arrows.operator("reorder.move_tab_down", text="", icon="TRIA_DOWN")
        # Apply Order button at the bottom
        layout.operator("reorder.apply_order", text="Apply Order & Save")
class REORDER_OT_move_tab_up(bpy.types.Operator):
    bl_idname = "reorder.move_tab_up"
    bl_label = "Move Tab Up"

    def execute(self, context):
        wm = context.window_manager
        idx = wm.npanel_tab_order_index
        if idx > 0:
            tabs = wm.npanel_tab_order
            tabs.move(idx, idx - 1)
            wm.npanel_tab_order_index = idx - 1
        return {'FINISHED'}

class REORDER_OT_move_tab_down(bpy.types.Operator):
    bl_idname = "reorder.move_tab_down"
    bl_label = "Move Tab Down"

    def execute(self, context):
        wm = context.window_manager
        idx = wm.npanel_tab_order_index
        tabs = wm.npanel_tab_order
        if idx < len(tabs) - 1:
            tabs.move(idx, idx + 1)
            wm.npanel_tab_order_index = idx + 1
        return {'FINISHED'}

class REORDER_OT_apply_order(bpy.types.Operator):
    bl_idname = "reorder.apply_order"
    bl_label = "Apply Tab Order"

    def execute(self, context):
        wm = context.window_manager
        order = [item.name for item in wm.npanel_tab_order]
        addon_dir = os.path.dirname(__file__)
        json_path = os.path.join(addon_dir, "tab_order.json")
        with open(json_path, "w") as f:
            json.dump(order, f)
        # Try to reorder the actual N-panel tabs by setting their bl_category order
        # This is a workaround: Blender does not support dynamic tab reordering natively, but we can try to unregister and re-register panels in the new order
        # Find all panels in the N-panel region
        panels = [panel for panel in bpy.types.Panel.__subclasses__() if getattr(panel, "bl_space_type", None) == "VIEW_3D" and getattr(panel, "bl_region_type", None) == "UI"]
        # Unregister all panels
        for panel in panels:
            try:
                bpy.utils.unregister_class(panel)
            except Exception:
                pass
        # Re-register panels in the order of tab names
        for tab_name in order:
            for panel in panels:
                if getattr(panel, "bl_category", None) == tab_name:
                    try:
                        bpy.utils.register_class(panel)
                    except Exception:
                        pass
        self.report({'INFO'}, "Tab order applied and saved!")
        return {'FINISHED'}

class REORDER_OT_refresh_tabs(bpy.types.Operator):
    bl_idname = "reorder.refresh_tabs"
    bl_label = "Refresh Tab List"

    def execute(self, context):
        wm = context.window_manager
        wm.npanel_tab_order.clear()
        # Get only unique tab titles (bl_category) from all panels in N-panel region
        categories = set()
        for panel in bpy.types.Panel.__subclasses__():
            if (
                getattr(panel, "bl_space_type", None) == "VIEW_3D" and
                getattr(panel, "bl_region_type", None) == "UI"
            ):
                cat = getattr(panel, "bl_category", None)
                if cat:
                    categories.add(cat)
        wm.npanel_tab_order.clear()
        for cat in sorted(categories):
            item = wm.npanel_tab_order.add()
            item.name = cat
        self.report({'INFO'}, "Tab titles refreshed!")
        return {'FINISHED'}

classes = [
    NPanelTabOrder,
    REORDER_UL_tab_order,
    REORDER_PT_npanel_tabs,
    REORDER_OT_apply_order,
    REORDER_OT_refresh_tabs,
    REORDER_OT_move_tab_up,
    REORDER_OT_move_tab_down
]

def load_tab_order(wm):
    addon_dir = os.path.dirname(__file__)
    json_path = os.path.join(addon_dir, "tab_order.json")
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            order = json.load(f)
        wm.npanel_tab_order.clear()
        for name in order:
            item = wm.npanel_tab_order.add()
            item.name = name

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.npanel_tab_order = bpy.props.CollectionProperty(type=NPanelTabOrder)
    bpy.types.WindowManager.npanel_tab_order_index = bpy.props.IntProperty()
    load_tab_order(bpy.context.window_manager)
    # Apply tab order to Blender panels on startup
    wm = bpy.context.window_manager
    order = [item.name for item in wm.npanel_tab_order]
    panels = [panel for panel in bpy.types.Panel.__subclasses__() if getattr(panel, "bl_space_type", None) == "VIEW_3D" and getattr(panel, "bl_region_type", None) == "UI"]
    # Unregister all panels
    for panel in panels:
        try:
            bpy.utils.unregister_class(panel)
        except Exception:
            pass
    # Re-register panels in the order of tab names
    for tab_name in order:
        for panel in panels:
            if getattr(panel, "bl_category", None) == tab_name:
                try:
                    bpy.utils.register_class(panel)
                except Exception:
                    pass

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.WindowManager.npanel_tab_order
    del bpy.types.WindowManager.npanel_tab_order_index

if __name__ == "__main__":
    register()
