#include <gtk/gtk.h>

GtkWidget *image;
GtkWidget *label;
gboolean timer_running = FALSE;
gdouble elapsed = 0.0;

gboolean update_frame(gpointer) {
    // 타이머만 업데이트
    if (timer_running) {
        elapsed += 0.1;
        int min = (int)(elapsed / 60);
        int sec = (int)elapsed % 60;
        int centi = (int)(elapsed * 10) % 10;

        char buf[64];
        snprintf(buf, sizeof(buf), "Time: %d:%02d.%d", min, sec, centi);
        gtk_label_set_text(GTK_LABEL(label), buf);
    }
    return TRUE;
}

void on_start(GtkButton *, gpointer) {
    timer_running = !timer_running;
}

void on_reset(GtkButton *, gpointer) {
    timer_running = FALSE;
    elapsed = 0.0;
    gtk_label_set_text(GTK_LABEL(label), "Time: 0:00.0");
}

void on_activate(GtkApplication *app, gpointer) {
    GtkWidget *win = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(win), "Camera Timer");
    gtk_window_set_default_size(GTK_WINDOW(win), 640, 520);

    GtkWidget *vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 5);
    gtk_container_add(GTK_CONTAINER(win), vbox);

    image = gtk_image_new_from_file("placeholder.png");
    gtk_box_pack_start(GTK_BOX(vbox), image, TRUE, TRUE, 0);

    label = gtk_label_new("Time: 0:00.0");
    gtk_box_pack_start(GTK_BOX(vbox), label, FALSE, FALSE, 0);

    GtkWidget *btn_start = gtk_button_new_with_label("Start / Pause");
    g_signal_connect(btn_start, "clicked", G_CALLBACK(on_start), NULL);
    gtk_box_pack_start(GTK_BOX(vbox), btn_start, FALSE, FALSE, 0);

    GtkWidget *btn_reset = gtk_button_new_with_label("Reset");
    g_signal_connect(btn_reset, "clicked", G_CALLBACK(on_reset), NULL);
    gtk_box_pack_start(GTK_BOX(vbox), btn_reset, FALSE, FALSE, 0);

    gtk_widget_show_all(win);
    g_timeout_add(100, update_frame, NULL);
}

int main(int argc, char **argv) {
    GtkApplication *app = gtk_application_new("com.example.cam", G_APPLICATION_FLAGS_NONE);
    g_signal_connect(app, "activate", G_CALLBACK(on_activate), NULL);
    int status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);
    return status;
}