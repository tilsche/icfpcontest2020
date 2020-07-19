#pragma once

#include <wx/aui/framemanager.h>
#include <wx/dcbuffer.h>
#include <wx/wx.h>

#include "interact.hpp"

class GalaxyApp : public wxApp
{
public:
    GalaxyApp() : wxApp(), interact_("galaxy")
    {
    }

    virtual bool OnInit();

private:
    zebra::Interact interact_;
};
class GalaxyFrame : public wxFrame
{
public:
    GalaxyFrame(zebra::Interact& interact);

private:
    void OnHello(wxCommandEvent& event);
    void OnExit(wxCommandEvent& event);
    void OnAbout(wxCommandEvent& event);

private:
    wxAuiManager aui_manager_;
};

class GalaxyPanel;

class GalaxyDC : public wxAutoBufferedPaintDC
{
public:
    GalaxyDC(GalaxyPanel* dp);
};

class GalaxyPanel : public wxPanel
{
public:
    GalaxyPanel(wxFrame* parent, zebra::Interact& interact) : wxPanel(parent), interact_(interact)
    {
        SetBackgroundStyle(wxBG_STYLE_CUSTOM);
        SetBackgroundColour(wxColor(100, 0, 100));
    }

    DECLARE_EVENT_TABLE()
private:
    void paint_event(wxPaintEvent& evt)
    {
        (void)evt;
        GalaxyDC dc(this);
        render(dc);
    }

    /*
     * Alternatively, you can use a clientDC to paint on the panel
     * at any time. Using this generally does not free you from
     * catching paint events, since it is possible that e.g. the window
     * manager throws away your drawing when the window comes to the
     * background, and expects you will redraw it when the window comes
     * back (by sending a paint event).
     *
     * In most cases, this will not be needed at all; simply handling
     * paint events and calling Refresh() when a refresh is needed
     * will do the job.
     */
    void paint_now()
    {
        GalaxyDC dc(this);
        render(dc);
    }

    void bounding_box(wxDC& dc);

    void render(wxDC& dc);

    wxPoint transform(zebra::Coordinate coord)
    {
        return wxPoint((coord.x + offset_x) * scale, (coord.y + offset_y) * scale);
    }

private:
    zebra::Interact& interact_;
    int scale = 5;
    wxCoord offset_x;
    wxCoord offset_y;
};

enum
{
    ID_Hello = 1
};
