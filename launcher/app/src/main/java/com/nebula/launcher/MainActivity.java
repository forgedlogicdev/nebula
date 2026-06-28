package com.nebula.launcher;

import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.*;
import java.util.*;

public class MainActivity extends Activity {

    private static final String TAG = "NEBULA";
    private static final String TERMUX_PKG = "com.termux";
    private static final String SPOTIFY_PKG = "com.spotify.music";
    private static final String MOONLIGHT_PKG = "com.limelight";

    private GridView appGrid;
    private AppAdapter appAdapter;
    private List<AppItem> apps;
    private HorizontalScrollView panelScroller;
    private int currentPanel = 2; // 0=code 1=games 2=home 3=music
    private int selectedAppIndex = 0;
    private static final int MATCH = ViewGroup.LayoutParams.MATCH_PARENT;
    private static final int WRAP = ViewGroup.LayoutParams.WRAP_CONTENT;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                             WindowManager.LayoutParams.FLAG_FULLSCREEN);

        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(0xFF050510);

        panelScroller = new HorizontalScrollView(this);
        panelScroller.setHorizontalScrollBarEnabled(false);
        panelScroller.setOverScrollMode(View.OVER_SCROLL_NEVER);

        LinearLayout panels = new LinearLayout(this);
        panels.setOrientation(LinearLayout.HORIZONTAL);
        panels.addView(buildCodePanel(), panelLP());
        panels.addView(buildGamesPanel(), panelLP());
        panels.addView(buildHomePanel(), panelLP());
        panels.addView(buildMusicPanel(), panelLP());
        panelScroller.addView(panels);
        root.addView(panelScroller);

        TextView hint = hint("L/R:switch panel | D-pad:move | A:open | B:home");
        FrameLayout.LayoutParams hp = new FrameLayout.LayoutParams(MATCH, WRAP);
        hp.gravity = Gravity.BOTTOM; hp.bottomMargin = dp(90);
        root.addView(hint, hp);
        root.addView(buildDock(), dockLP());

        setContentView(root);
        panelScroller.post(() -> panelScroller.scrollTo(sw() * 2, 0));
        loadApps();
        registerPackageReceiver();
    }

    private LinearLayout.LayoutParams panelLP() {
        return new LinearLayout.LayoutParams(sw(), MATCH);
    }

    // ══════ PANELS ══════════════════════════════════════════════════

    private View buildHomePanel() {
        LinearLayout home = vbox(dp(16), dp(44), dp(16), dp(16));
        home.addView(emoji("\uD83D\uDC7D", 48), lp(MATCH, WRAP, 0, 20, 0, 0));
        home.addView(pill("Search...", 0x30ffffff, dp(20), 0x0d111111),
            lp(MATCH, dp(42), 0, 16, 0, 0));

        appGrid = new GridView(this);
        appGrid.setNumColumns(4);
        appGrid.setVerticalSpacing(dp(12)); appGrid.setHorizontalSpacing(dp(4));
        appGrid.setPadding(dp(4), dp(12), dp(4), dp(12));
        appGrid.setStretchMode(GridView.STRETCH_COLUMN_WIDTH);
        appGrid.setSelector(new ColorDrawable(0x154a6af0));
        home.addView(appGrid, lp(MATCH, 0, 0, 8, 0, 0, 1));
        appGrid.setOnItemClickListener((p, v, pos, id) -> {
            if (pos < apps.size()) launchApp(apps.get(pos));
        });
        return home;
    }

    private View buildGamesPanel() {
        LinearLayout panel = vbox(dp(16), dp(60), dp(16), dp(16));
        panel.addView(label("GAMES HUB", 0x40ff6b9d), lp(MATCH, WRAP, 0, 0, 0, 12));

        GradientDrawable card = new GradientDrawable();
        card.setCornerRadius(dp(16)); card.setColor(0x15ff6b9d);

        LinearLayout info = new LinearLayout(this);
        info.setOrientation(LinearLayout.VERTICAL);
        info.setBackground(card);
        info.setPadding(dp(16), dp(16), dp(16), dp(16));

        info.addView(label("HP MINI SERVER", 0x80ff6b9d), lp(MATCH, WRAP, 0, 0, 0, 4));
        info.addView(small("10.0.0.108:47989 (Sunshine v0.23.1)", 0x40ffffff));
        info.addView(small("Intel i5-7500T | HD Graphics 630 | 11GB", 0x30ffffff));
        panel.addView(info, lp(MATCH, WRAP, 0, 12, 0, 0));

        panel.addView(btn("LAUNCH MOONLIGHT", 0xff1ed760, 0x221ed760, () -> {
            Intent i = getPackageManager().getLaunchIntentForPackage(MOONLIGHT_PKG);
            if (i != null) startActivity(i);
            else Toast.makeText(this, "Moonlight not installed", Toast.LENGTH_SHORT).show();
        }), lp(MATCH, dp(48), 0, 8, 0, 0));

        panel.addView(btn("HOST WEB UI", 0xffff9e64, 0x22ff9e64, () -> {
            startActivity(new Intent(Intent.ACTION_VIEW,
                Uri.parse("https://10.0.0.108:47990")));
        }), lp(MATCH, dp(48), 0, 8, 0, 0));

        panel.addView(label("READY GAMES", 0x30ffffff), lp(MATCH, WRAP, 0, 20, 0, 8));

        String[][] games = {
            {"\uD83D\uDDA5  Terminal", ""},
            {"\uD83C\uDFAE  RetroArch", "RetroArch"},
            {"\uD83C\uDF0D  Terraria", "Terraria.sh"},
            {"\uD83D\uDDE1  OpenTTD", "openttd"},
            {"\uD83D\uDD79  Stardew Valley", "StardewValley"},
        };
        for (String[] g : games) {
            panel.addView(btn(g[0], 0x60ffffff, 0x0dffffff, () -> {
                Toast.makeText(this, "Install: " + g[1], Toast.LENGTH_SHORT).show();
            }), lp(MATCH, dp(40), 0, 4, 0, 0));
        }

        return panel;
    }

    private View buildCodePanel() {
        LinearLayout panel = vbox(dp(20), dp(60), dp(20), dp(20));
        panel.addView(label("CODE PANEL", 0x4000ff99), lp(MATCH, WRAP, 0, 0, 0, 16));

        TextView term = new TextView(this);
        term.setText("root@nebula ~ $ cargo build\n  Compiling nebula v0.1.0\n  Compiling gl-render v0.9.1\n  Finished release in 2.4s\n\nroot@nebula ~ $ _");
        term.setTextColor(0x88b4dcc8); term.setTextSize(11);
        term.setTypeface(android.graphics.Typeface.MONOSPACE);
        term.setPadding(dp(16), dp(16), dp(16), dp(16));
        term.setBackgroundColor(0x22000000);
        panel.addView(term);
        panel.addView(btn("[ TERMUX ]", 0x8800ff99, 0x1100ff99,
            () -> launchPkg(TERMUX_PKG)), lp(WRAP, WRAP, 0, 20, 0, 0));
        return panel;
    }

    private View buildMusicPanel() {
        LinearLayout panel = vbox(dp(20), dp(60), dp(20), dp(20));
        panel.setGravity(Gravity.CENTER_HORIZONTAL);
        panel.addView(emoji("\uD83D\uDC7D", 72));
        panel.addView(label("NOW PLAYING", 0x30b478f0), lp(MATCH, WRAP, 0, 24, 0, 0));

        TextView song = new TextView(this);
        song.setText("Resonance"); song.setTextColor(0xccffffff);
        song.setTextSize(20); song.setGravity(Gravity.CENTER);
        panel.addView(song, lp(MATCH, WRAP, 0, 8, 0, 0));
        panel.addView(small("HOME", 0x40ffffff), lp(MATCH, WRAP, 0, 4, 0, 0));
        panel.addView(btn("[ SPOTIFY ]", 0x881ed760, 0x111ed760,
            () -> launchPkgOrUrl(SPOTIFY_PKG, "https://open.spotify.com")),
            lp(WRAP, WRAP, 0, 32, 0, 0));
        return panel;
    }

    private View buildDock() {
        LinearLayout dock = new LinearLayout(this);
        dock.setOrientation(LinearLayout.HORIZONTAL); dock.setGravity(Gravity.CENTER);
        GradientDrawable bg = new GradientDrawable();
        bg.setCornerRadius(dp(20)); bg.setColor(0x0d111111);
        dock.setBackground(bg); dock.setPadding(dp(4), 0, dp(4), 0);

        int[] icons = { android.R.drawable.ic_dialog_email,
                        android.R.drawable.ic_menu_edit,
                        android.R.drawable.ic_media_play,
                        android.R.drawable.ic_menu_compass };
        Runnable[] actions = {
            () -> startActivity(new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_APP_MESSAGING)),
            () -> launchPkg(TERMUX_PKG),
            () -> launchPkgOrUrl(SPOTIFY_PKG, "https://open.spotify.com"),
            () -> startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://google.com")))
        };
        for (int i = 0; i < 4; i++) {
            ImageView iv = new ImageView(this);
            iv.setImageResource(icons[i]); iv.setColorFilter(0x60ffffff);
            iv.setPadding(dp(12), dp(12), dp(12), dp(12));
            final int idx = i; iv.setOnClickListener(v -> actions[idx].run());
            dock.addView(iv, new LinearLayout.LayoutParams(0, dp(56), 1));
        }
        return dock;
    }

    // ══════ KEY HANDLING ═══════════════════════════════════════════

    @Override
    public boolean dispatchKeyEvent(KeyEvent event) {
        if (event.getAction() != KeyEvent.ACTION_DOWN || event.getRepeatCount() > 0)
            return super.dispatchKeyEvent(event);

        switch (event.getKeyCode()) {
            case KeyEvent.KEYCODE_BUTTON_A:
                if (currentPanel == 2 && selectedAppIndex < apps.size())
                    launchApp(apps.get(selectedAppIndex));
                Toast.makeText(this, "A", Toast.LENGTH_SHORT).show();
                return true;
            case KeyEvent.KEYCODE_BUTTON_B:
                switchToPanel(2);
                Toast.makeText(this, "B - home", Toast.LENGTH_SHORT).show();
                return true;
            case KeyEvent.KEYCODE_BUTTON_X:
                launchPkg(TERMUX_PKG);
                Toast.makeText(this, "X - termux", Toast.LENGTH_SHORT).show();
                return true;
            case KeyEvent.KEYCODE_BUTTON_Y:
                switchToPanel(3);
                Toast.makeText(this, "Y - music", Toast.LENGTH_SHORT).show();
                return true;
            case KeyEvent.KEYCODE_DPAD_LEFT:
                if (currentPanel == 2) moveSelection(-1, 0);
                else if (currentPanel > 0) switchToPanel(currentPanel - 1);
                return true;
            case KeyEvent.KEYCODE_DPAD_RIGHT:
                if (currentPanel == 2) moveSelection(1, 0);
                else if (currentPanel < 3) switchToPanel(currentPanel + 1);
                return true;
            case KeyEvent.KEYCODE_DPAD_UP:
                if (currentPanel == 2) moveSelection(0, -1);
                return true;
            case KeyEvent.KEYCODE_DPAD_DOWN:
                if (currentPanel == 2) moveSelection(0, 1);
                return true;
            case KeyEvent.KEYCODE_BUTTON_L1:
                switchToPanel(1);
                Toast.makeText(this, "L - games", Toast.LENGTH_SHORT).show();
                return true;
            case KeyEvent.KEYCODE_BUTTON_R1:
                switchToPanel(3);
                Toast.makeText(this, "R - music", Toast.LENGTH_SHORT).show();
                return true;
            case KeyEvent.KEYCODE_BUTTON_L2:
                expandStatusBar();
                return true;
            case KeyEvent.KEYCODE_DPAD_CENTER:
            case KeyEvent.KEYCODE_BUTTON_START:
                switchToPanel(2);
                return true;
        }
        return super.dispatchKeyEvent(event);
    }

    private void switchToPanel(int p) {
        if (p >= 0 && p <= 3 && p != currentPanel) {
            currentPanel = p;
            panelScroller.smoothScrollTo(p * sw(), 0);
        }
    }

    private void moveSelection(int dx, int dy) {
        if (currentPanel != 2 || apps.isEmpty()) return;
        int cols = 4, row = selectedAppIndex / cols, col = selectedAppIndex % cols;
        col = Math.max(0, Math.min(cols - 1, col + dx));
        row = Math.max(0, Math.min((apps.size() - 1) / cols, row + dy));
        selectedAppIndex = row * cols + col;
        if (selectedAppIndex >= apps.size()) selectedAppIndex = apps.size() - 1;
        if (appGrid != null) appGrid.setSelection(selectedAppIndex);
    }

    private void expandStatusBar() {
        try {
            Object sbs = getSystemService("statusbar");
            if (sbs != null) sbs.getClass().getMethod("expandNotificationsPanel").invoke(sbs);
        } catch (Exception ignored) {}
    }

    // ══════ APP MANAGEMENT ══════════════════════════════════════════

    private void loadApps() {
        apps = new ArrayList<>();
        PackageManager pm = getPackageManager();
        Intent main = new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER);
        for (ResolveInfo ri : pm.queryIntentActivities(main, 0)) {
            AppItem a = new AppItem();
            a.label = ri.loadLabel(pm).toString();
            a.icon = ri.loadIcon(pm);
            a.packageName = ri.activityInfo.packageName;
            a.activityName = ri.activityInfo.name;
            apps.add(a);
        }
        appAdapter = new AppAdapter();
        appGrid.setAdapter(appAdapter);
        selectedAppIndex = 0;
    }

    private void launchApp(AppItem item) {
        Intent i = new Intent(Intent.ACTION_MAIN);
        i.addCategory(Intent.CATEGORY_LAUNCHER);
        i.setClassName(item.packageName, item.activityName);
        i.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(i);
    }

    private void launchPkg(String pkg) {
        Intent i = getPackageManager().getLaunchIntentForPackage(pkg);
        if (i != null) startActivity(i);
        else Toast.makeText(this, pkg + " not found", Toast.LENGTH_SHORT).show();
    }

    private void launchPkgOrUrl(String pkg, String url) {
        Intent i = getPackageManager().getLaunchIntentForPackage(pkg);
        if (i != null) startActivity(i);
        else startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
    }

    private void registerPackageReceiver() {
        IntentFilter f = new IntentFilter();
        f.addAction(Intent.ACTION_PACKAGE_ADDED);
        f.addAction(Intent.ACTION_PACKAGE_REMOVED);
        f.addDataScheme("package");
        registerReceiver(packageReceiver, f);
    }

    private BroadcastReceiver packageReceiver = new BroadcastReceiver() {
        @Override public void onReceive(Context ctx, Intent i) { loadApps(); }
    };

    @Override protected void onDestroy() {
        super.onDestroy();
        try { unregisterReceiver(packageReceiver); } catch (Exception ignored) {}
    }

    // ══════ UTILITY ══════════════════════════════════════════════════

    private int sw() { return getResources().getDisplayMetrics().widthPixels; }
    private int dp(int dp) { return (int)(dp * getResources().getDisplayMetrics().density + 0.5f); }

    private LinearLayout.LayoutParams lp(int w, int h, int l, int t, int r, int b) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(w, h);
        p.setMargins(dp(l), dp(t), dp(r), dp(b)); return p;
    }
    private LinearLayout.LayoutParams lp(int w, int h, int l, int t, int r, int b, float wt) {
        LinearLayout.LayoutParams p = lp(w, h, l, t, r, b); p.weight = wt; return p;
    }
    private FrameLayout.LayoutParams dockLP() {
        FrameLayout.LayoutParams p = new FrameLayout.LayoutParams(MATCH, dp(70));
        p.gravity = Gravity.BOTTOM; p.bottomMargin = dp(14);
        p.leftMargin = dp(20); p.rightMargin = dp(20); return p;
    }

    private LinearLayout vbox(int l, int t, int r, int b) {
        LinearLayout ll = new LinearLayout(this);
        ll.setOrientation(LinearLayout.VERTICAL);
        ll.setPadding(dp(l), dp(t), dp(r), dp(b));
        return ll;
    }
    private TextView label(String text, int color) {
        TextView t = new TextView(this); t.setText(text);
        t.setTextColor(color); t.setTextSize(10);
        t.setGravity(Gravity.CENTER); return t;
    }
    private TextView small(String text, int color) {
        TextView t = new TextView(this); t.setText(text);
        t.setTextColor(color); t.setTextSize(9); return t;
    }
    private TextView hint(String text) {
        TextView t = new TextView(this); t.setText(text);
        t.setTextColor(0x15ffffff); t.setTextSize(8);
        t.setGravity(Gravity.CENTER); return t;
    }
    private TextView emoji(String text, int size) {
        TextView t = new TextView(this); t.setText(text);
        t.setTextSize(size); t.setGravity(Gravity.CENTER); return t;
    }
    private TextView pill(String text, int color, int radius, int bg) {
        TextView t = new TextView(this); t.setText(text);
        t.setTextColor(color); t.setPadding(dp(18), dp(10), dp(18), dp(10));
        GradientDrawable gd = new GradientDrawable();
        gd.setCornerRadius(radius); gd.setColor(bg); t.setBackground(gd);
        return t;
    }
    private TextView btn(String text, int textColor, int bgColor, Runnable action) {
        TextView t = new TextView(this); t.setText(text);
        t.setTextColor(textColor); t.setGravity(Gravity.CENTER);
        GradientDrawable gd = new GradientDrawable();
        gd.setCornerRadius(dp(8)); gd.setColor(bgColor);
        t.setBackground(gd); t.setPadding(dp(16), dp(10), dp(16), dp(10));
        t.setOnClickListener(v -> action.run()); return t;
    }

    class AppItem { String label, packageName, activityName; android.graphics.drawable.Drawable icon; }

    class AppAdapter extends BaseAdapter {
        @Override public int getCount() { return apps.size(); }
        @Override public Object getItem(int i) { return apps.get(i); }
        @Override public long getItemId(int i) { return i; }
        @Override
        public View getView(int pos, View convertView, ViewGroup parent) {
            if (convertView == null) {
                LinearLayout ll = new LinearLayout(MainActivity.this);
                ll.setOrientation(LinearLayout.VERTICAL);
                ll.setGravity(Gravity.CENTER);
                ll.setPadding(dp(4), dp(8), dp(4), dp(8));
                ImageView iv = new ImageView(MainActivity.this); iv.setId(1);
                ll.addView(iv, new LinearLayout.LayoutParams(dp(48), dp(48)));
                TextView tv = new TextView(MainActivity.this); tv.setId(2);
                tv.setTextSize(10); tv.setTextColor(0x80ffffff);
                tv.setSingleLine(); tv.setGravity(Gravity.CENTER);
                tv.setMaxWidth(dp(68));
                ll.addView(tv, new LinearLayout.LayoutParams(dp(68), WRAP));
                ((LinearLayout.LayoutParams) tv.getLayoutParams()).topMargin = dp(4);
                convertView = ll;
            }
            AppItem item = apps.get(pos);
            ((ImageView) convertView.findViewById(1)).setImageDrawable(item.icon);
            ((TextView) convertView.findViewById(2)).setText(item.label);
            return convertView;
        }
    }
}
