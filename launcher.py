#!/usr/bin/env python3
#
# Game Launcher
#
# Copyright (C) 2026
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
import gi, os, json, subprocess, shlex, uuid
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Gio, GLib, GdkPixbuf

APP_DIR=os.path.expanduser("~/.config/game-launcher")
DATA_FILE=os.path.join(APP_DIR,"games.json")
os.makedirs(APP_DIR, exist_ok=True)

DEFAULT_CMD='sh -c "cd ~/.wine/drive_c/GAMEFOLDER && wine GAME.exe"'

def load_games():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: return []

def save_games(games):
    with open(DATA_FILE,"w",encoding="utf-8") as f: json.dump(games,f,indent=2,ensure_ascii=False)

class GameDialog(Gtk.Dialog):
    def __init__(self,parent,game=None):
        super().__init__(title="Game", transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OK,Gtk.ResponseType.OK)
        box=self.get_content_area(); grid=Gtk.Grid(column_spacing=8,row_spacing=8,margin=12); box.add(grid)
        self.entries={}
        fields=[("name","Name"),("type","Type"),("cover","Cover image"),("command","Command"),("prefix","Wine prefix"),("description","Description")]
        for i,(key,label) in enumerate(fields):
            grid.attach(Gtk.Label(label=label,xalign=0),0,i,1,1)
            if key == "cover":
                row=Gtk.Box(spacing=6)
                e=Gtk.Entry(); e.set_hexpand(True)
                row.pack_start(e,True,True,0)
                browse=Gtk.Button(label="Browse…")
                browse.set_tooltip_text("Choose a cover image")
                browse.connect("clicked", self.choose_cover, e)
                row.pack_start(browse,False,False,0)
                grid.attach(row,1,i,1,1)
            elif key == "command":
                row=Gtk.Box(spacing=6)
                e=Gtk.Entry(); e.set_hexpand(True)
                row.pack_start(e,True,True,0)
                browse=Gtk.Button(label="Browse…")
                browse.set_tooltip_text("Select the game's executable file")
                browse.connect("clicked", self.choose_executable, e)
                row.pack_start(browse,False,False,0)
                grid.attach(row,1,i,1,1)
            else:
                e=Gtk.Entry(); e.set_hexpand(True); grid.attach(e,1,i,1,1)
            self.entries[key]=e
        if game:
            for k,e in self.entries.items(): e.set_text(game.get(k,""))
        else:
            self.entries["command"].set_text(DEFAULT_CMD)
            self.entries["prefix"].set_text(os.path.expanduser("~/.wine"))
        self.show_all()
    def choose_cover(self, button, entry):
        dialog=Gtk.FileChooserDialog(
            title="Select a cover image",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        dialog.set_local_only(True)
        filt=Gtk.FileFilter(); filt.set_name("Images"); filt.add_mime_type("image/png"); filt.add_mime_type("image/jpeg"); filt.add_mime_type("image/webp"); filt.add_mime_type("image/gif"); filt.add_pattern("*.jpg"); filt.add_pattern("*.jpeg"); filt.add_pattern("*.png"); filt.add_pattern("*.webp"); filt.add_pattern("*.gif")
        dialog.add_filter(filt)
        allf=Gtk.FileFilter(); allf.set_name("All files"); allf.add_pattern("*"); dialog.add_filter(allf)
        if entry.get_text().strip():
            try: dialog.set_filename(os.path.expanduser(entry.get_text().strip()))
            except Exception: pass
        if dialog.run() == Gtk.ResponseType.OK:
            entry.set_text(dialog.get_filename())
        dialog.destroy()
    def choose_executable(self, button, entry):
        dialog=Gtk.FileChooserDialog(
            title="Select the game's executable file",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        dialog.set_local_only(True)
        if dialog.run() == Gtk.ResponseType.OK:
            path=dialog.get_filename()
            directory=os.path.dirname(path) or "."
            filename=os.path.basename(path)
            # Keep the architecture sh -c "cd ... && wine ...".
            entry.set_text('sh -c "cd %s && wine %s"' % (shlex.quote(directory), shlex.quote(filename)))
        dialog.destroy()

    def get_game(self):
        return {k:e.get_text().strip() for k,e in self.entries.items()}

# Wine Tools
class SettingsDialog(Gtk.Dialog):
    def __init__(self,parent):
        super().__init__(title="Wine tools",transient_for=parent,flags=0)
        box=self.get_content_area(); box.set_margin_top(12); box.set_margin_bottom(12)
        tools=[("winecfg","winecfg"),("winetricks","winetricks"),("Wine Uninstaller","wine uninstaller"),("Registry","wine regedit"),("File Explorer","wine explorer"),("Task Manager","wine taskmgr")]
        for label,cmd in tools:
            b=Gtk.Button(label=label); b.set_margin_start(12); b.set_margin_end(12); b.connect("clicked",self.run_tool,cmd); box.pack_start(b,False,False,3)
        self.show_all()
    def run_tool(self,button,cmd):
        try: subprocess.Popen(shlex.split(cmd), start_new_session=True)
        except Exception as e: self.parent_message(str(e))
    def parent_message(self,msg): pass

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Game Launcher",default_width=900,default_height=600)
        self.games=load_games(); self.sort_key="name"; self.view_mode="grid"; self.zoom="small"
        self.connect("destroy",Gtk.main_quit)
        root=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6); self.add(root)
        toolbar=Gtk.Box(spacing=6); toolbar.set_margin_start(8); toolbar.set_margin_end(8)
        root.pack_start(toolbar,False,False,6)
        add=Gtk.Button(label="＋ Add"); add.connect("clicked",self.add_game); toolbar.pack_start(add,False,False,0)
        edit=Gtk.Button(label="Modify"); edit.connect("clicked",self.edit_game); toolbar.pack_start(edit,False,False,0)
        delete=Gtk.Button(label="Remove"); delete.connect("clicked",self.delete_game); toolbar.pack_start(delete,False,False,0)
        wine=Gtk.Button(label="Wine tools"); wine.connect("clicked",lambda *_:SettingsDialog(self).run()); toolbar.pack_end(wine,False,False,0)
        self.view_list=Gtk.Button(); self.view_list.set_image(Gtk.Image.new_from_icon_name("view-list",Gtk.IconSize.BUTTON)); self.view_list.set_tooltip_text("List view"); self.view_list.connect("clicked",lambda *_:self.set_view("list")); toolbar.pack_end(self.view_list,False,False,0)
        self.view_grid=Gtk.Button(); self.view_grid.set_image(Gtk.Image.new_from_icon_name("view-grid",Gtk.IconSize.BUTTON)); self.view_grid.set_tooltip_text("Grid view"); self.view_grid.connect("clicked",lambda *_:self.set_view("grid")); toolbar.pack_end(self.view_grid,False,False,0)
        self.zoom_combo=Gtk.ComboBoxText()
        for x in ["Small size","Medium size","Large size"]: self.zoom_combo.append_text(x)
        self.zoom_combo.set_active(1); self.zoom_combo.set_tooltip_text("Item size"); self.zoom_combo.connect("changed",self.change_zoom); toolbar.pack_end(self.zoom_combo,False,False,0)
        self.search=Gtk.SearchEntry(); self.search.set_placeholder_text("Search…"); self.search.connect("search-changed",lambda *_:self.refresh()); toolbar.pack_end(self.search,False,False,0)
        self.combo=Gtk.ComboBoxText()
        self.combo.append_text("A–Z")
        self.combo.append_text("Type")
        self.combo.append_text("Date")
        self.combo.set_active(0); self.combo.set_tooltip_text("Sort games"); self.combo.connect("changed",self.change_sort); toolbar.pack_end(self.combo,False,False,0)
        self.list=Gtk.ListBox(); self.list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.grid=Gtk.FlowBox(); self.grid.set_selection_mode(Gtk.SelectionMode.SINGLE); self.grid.set_max_children_per_line(6); self.grid.set_min_children_per_line(1); self.grid.set_row_spacing(4); self.grid.set_column_spacing(4); self.grid.set_margin_top(4); self.grid.set_margin_bottom(4); self.grid.set_margin_start(4); self.grid.set_margin_end(4)
        css=Gtk.CssProvider()
        css.load_from_data(b"""
        flowboxchild {
            padding: 5px 0px;
            margin: 0px;
        }
        flowboxchild:selected {
            outline-offset: 0px;
        }
        """)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.stack=Gtk.Stack(); self.stack.add_named(self.list,"list"); self.stack.add_named(self.grid,"grid")
        scroll=Gtk.ScrolledWindow(); scroll.add(self.stack); root.pack_start(scroll,True,True,0)
        self.refresh(); self.show_all()
    def change_sort(self,c):
        self.sort_key={"A–Z":"name","Type":"type","Date":"id"}[c.get_active_text()]; self.refresh()
    def set_view(self, mode):
        self.view_mode=mode; self.stack.set_visible_child_name(mode); self.refresh()
    def change_zoom(self, combo):
        self.zoom={"Small size":"small","Medium size":"medium","Large size":"large"}[combo.get_active_text()]
        self.refresh()
    def sizes(self):
        return {"small":(90,130),"medium":(120,175),"large":(160,230)}[self.zoom]
    def load_cover(self, path, size):
        try:
            pb=GdkPixbuf.Pixbuf.new_from_file(os.path.expanduser(path))
            w,h=pb.get_width(),pb.get_height()
            scale=min(float(size)/w, float(size)/h)
            nw=max(1,int(w*scale)); nh=max(1,int(h*scale))
            return pb.scale_simple(nw,nh,GdkPixbuf.InterpType.BILINEAR)
        except Exception:
            return None
    def grid_title(self, name):
        name = name or "Untitled"
        return "\n".join(name[i:i+20] for i in range(0, len(name), 20))

    def selected(self):
        row = self.list.get_selected_row() if self.view_mode == "list" else self.grid.get_selected_children()[0] if self.grid.get_selected_children() else None
        return row.game if row else None
    def refresh(self):
        for r in self.list.get_children(): self.list.remove(r)
        for r in self.grid.get_children(): self.grid.remove(r)
        list_px, grid_px = self.sizes()
        q=self.search.get_text().lower()
        games=[g for g in self.games if q in g.get("name","").lower() or q in g.get("type","").lower()]
        games.sort(key=lambda g:g.get(self.sort_key,"").lower() if isinstance(g.get(self.sort_key,""),str) else g.get(self.sort_key,0))
        for g in games:
            if self.view_mode == "list":
                row=Gtk.ListBoxRow(); row.game=g
                h=Gtk.Box(spacing=12,margin=8)
                cover_w, cover_h = list_px, int(list_px * 1.45)
                frame=Gtk.Alignment.new(0.5,0.5,0,0)
                frame.set_size_request(cover_w, cover_h)
                img=Gtk.Image()
                if g.get("cover") and os.path.exists(os.path.expanduser(g["cover"])):
                    pb=GdkPixbuf.Pixbuf.new_from_file(os.path.expanduser(g["cover"]))
                    scale=min(float(cover_w)/pb.get_width(), float(cover_h)/pb.get_height())
                    nw=max(1,int(pb.get_width()*scale)); nh=max(1,int(pb.get_height()*scale))
                    frame.add(Gtk.Image.new_from_pixbuf(pb.scale_simple(nw,nh,GdkPixbuf.InterpType.BILINEAR)))
                else:
                    img.set_from_icon_name("applications-games",Gtk.IconSize.DIALOG)
                    frame.add(img)
                h.pack_start(frame,False,False,0)

                info=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=4)
                info.set_valign(Gtk.Align.FILL)
                info.set_size_request(0,cover_h)
                info.pack_start(Gtk.Label(label=g.get("name","Untitled"),xalign=0),False,False,0)
                info.pack_start(Gtk.Label(label=g.get("type",""),xalign=0),False,False,0)

                desc=Gtk.Label(label=g.get("description",""),xalign=0)
                desc.set_line_wrap(True)
                desc.set_max_width_chars(60)
                desc.set_valign(Gtk.Align.START)
                info.pack_start(desc,True,True,0)
                h.pack_start(info,True,True,8)

                run_area=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                run_area.set_size_request(110,cover_h)
                run_area.set_valign(Gtk.Align.FILL)

                b=Gtk.Button(label="Run")
                b.connect("clicked",self.launch,g)
                b.set_halign(Gtk.Align.CENTER)
                b.set_valign(Gtk.Align.CENTER)
                run_area.pack_start(b,True,True,0)

                separator=Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
                h.pack_start(separator,False,False,8)
                h.pack_start(run_area,False,False,0)

                row.add(h); self.list.add(row)
            else:
                child=Gtk.FlowBoxChild(); child.game=g
                child.set_halign(Gtk.Align.FILL)
                child.set_valign(Gtk.Align.START)
                child.set_margin_top(0); child.set_margin_bottom(0)
                child.set_margin_start(0); child.set_margin_end(0)
                box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=5)
                box.set_halign(Gtk.Align.CENTER)
                box.set_valign(Gtk.Align.START)
                img=Gtk.Image()
                cover_path=os.path.expanduser(g.get("cover","")) if g.get("cover") else ""
                if cover_path and os.path.exists(cover_path):
                    pb=GdkPixbuf.Pixbuf.new_from_file(cover_path)
                    box_w, box_h = grid_px, int(grid_px * 1.45)
                    scale=min(float(box_w)/pb.get_width(), float(box_h)/pb.get_height())
                    nw=max(1,int(pb.get_width()*scale)); nh=max(1,int(pb.get_height()*scale))
                    scaled=pb.scale_simple(nw,nh,GdkPixbuf.InterpType.BILINEAR)
                    frame=Gtk.Alignment.new(0.5,0.5,0,0)
                    frame.set_size_request(box_w, box_h)
                    frame.add(Gtk.Image.new_from_pixbuf(scaled))
                    box.pack_start(frame,False,False,0)
                    child.set_size_request(box_w+8,-1)
                else:
                    box_w, box_h = grid_px, int(grid_px * 1.45)
                    frame=Gtk.Alignment.new(0.5,0.5,0,0)
                    frame.set_size_request(box_w, box_h)
                    img.set_from_icon_name("applications-games",Gtk.IconSize.DIALOG)
                    frame.add(img)
                    box.pack_start(frame,False,False,0)
                    child.set_size_request(box_w+8,-1)
                title=Gtk.Label(label=self.grid_title(g.get("name","Untitled")),xalign=0.5)
                title.set_line_wrap(False)
                title.set_justify(Gtk.Justification.CENTER)
                title.set_max_width_chars(20)
                title.set_width_chars(20)
                box.pack_start(title,False,False,0)
                b=Gtk.Button(label="Run"); b.connect("clicked",self.launch,g); box.pack_start(b,False,False,0); child.add(box); self.grid.add(child)
        self.list.show_all(); self.grid.show_all(); self.stack.set_visible_child_name(self.view_mode)
    def add_game(self,*_):
        d=GameDialog(self); r=d.run()
        if r==Gtk.ResponseType.OK:
            g=d.get_game(); g["id"]=len(self.games)+1; self.games.append(g); save_games(self.games); self.refresh()
        d.destroy()
    def edit_game(self,*_):
        g=self.selected()
        if not g:return
        d=GameDialog(self,g); r=d.run()
        if r==Gtk.ResponseType.OK: g.update(d.get_game()); save_games(self.games); self.refresh()
        d.destroy()
    def delete_game(self,*_):
        g=self.selected()
        if not g:
            return
        md=Gtk.MessageDialog(self,0,Gtk.MessageType.WARNING,Gtk.ButtonsType.NONE,
                             "Remove game?")
        md.format_secondary_text('Are you sure you want to remove "%s"?' % g.get("name","Untitled"))
        md.add_button(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL)
        md.add_button(Gtk.STOCK_REMOVE,Gtk.ResponseType.OK)
        response=md.run()
        md.destroy()
        if response == Gtk.ResponseType.OK:
            self.games.remove(g)
            save_games(self.games)
            self.refresh()
    def launch(self,button,g):
        cmd=g.get("command",DEFAULT_CMD)
        env=os.environ.copy()
        if g.get("prefix"): env["WINEPREFIX"]=os.path.expanduser(g["prefix"])
        try: subprocess.Popen(cmd,shell=True,env=env,start_new_session=True)
        except Exception as e:
            md=Gtk.MessageDialog(self,0,Gtk.MessageType.ERROR,Gtk.ButtonsType.OK,str(e)); md.run(); md.destroy()

if __name__=="__main__": MainWindow(); Gtk.main()
