import gi
import logging

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk, Gtk  # noqa

log = logging.getLogger(__name__)


class UrouteGui(Gtk.Window):
    def __init__(self, uroute):
        super(UrouteGui, self).__init__()
        self.uroute = uroute
        self.command = None
        self._build_ui()

    def run(self):
        self.show_all()
        Gtk.main()
        return self.command

    def _build_ui(self):
        # Init main window
        self.set_title('Link Dispatcher')
        self.set_border_width(10)
        self.set_default_size(400, 300)
        self.connect('destroy', self._on_cancel_clicked)
        self.connect('key-press-event', self._on_key_pressed)

        vbox = Gtk.VBox(spacing=6)
        self.add(vbox)

        self.url_label = Gtk.Label()
        self.url_label.set_markup('<tt>{}</tt>'.format(self.uroute.url))
        self.command_entry = Gtk.Entry()

        vbox.pack_start(self.url_label, False, False, 0)
        vbox.pack_start(self._build_browser_list(), True, True, 0)
        vbox.pack_start(self.command_entry, False, False, 0)
        vbox.pack_start(self._build_button_toolbar(), False, False, 0)

    def _build_browser_list(self):
        self.browser_store = Gtk.ListStore(str, str)

        default_itr = None
        default_program = self.uroute.programs.get(self.uroute.default_program)

        for program in self.uroute.programs.values():
            itr = self.browser_store.append([program.name, program.command])
            if program is default_program:
                default_itr = itr

        self.browser_list = Gtk.TreeView(self.browser_store)
        self.browser_list.append_column(
            Gtk.TreeViewColumn('Browser', Gtk.CellRendererText(), text=0),
        )

        selection = self.browser_list.get_selection()
        selection.connect('changed', self._on_browser_selection_change)
        if default_itr:
            selection.select_iter(default_itr)

        return self.browser_list

    def _build_button_toolbar(self):
        hbox = Gtk.Box(spacing=6)

        button = Gtk.Button.new_with_mnemonic('Run')
        button.connect('clicked', self._on_run_clicked)
        hbox.pack_end(button, False, False, 0)

        button = Gtk.Button.new_with_label('Cancel')
        button.connect('clicked', self._on_cancel_clicked)
        hbox.pack_end(button, False, False, 0)

        return hbox

    def _on_browser_selection_change(self, selection):
        model, sel_iter = selection.get_selected()
        self.command_entry.set_text(model.get_value(sel_iter, 1))

    def _on_cancel_clicked(self, _button):
        self.command = None
        self.hide()
        Gtk.main_quit()

    def _on_run_clicked(self, _button):
        self.command = self.command_entry.get_text()

        model, sel_iter = self.browser_list.get_selection().get_selected()
        log.debug('Selected browser: %s', model.get_value(sel_iter, 0))

        self.hide()
        Gtk.main_quit()

    def _on_key_pressed(self, wnd, event):
        if event.keyval == Gdk.KEY_Escape:
            self._on_cancel_clicked(None)
        if event.keyval == Gdk.KEY_Return:
            self._on_run_clicked(None)