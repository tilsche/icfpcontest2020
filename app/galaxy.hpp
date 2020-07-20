#pragma once

#include <optional>

#include <wx/aui/framemanager.h>
#include <wx/dcbuffer.h>
#include <wx/wx.h>

#include "alien.hpp"
#include "interact.hpp"
#include "riddle.hpp"

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
    void on_try_all(wxCommandEvent& event);
    void on_try_6(wxCommandEvent& event);
    void on_undo(wxCommandEvent& event);
    void on_save_trace(wxCommandEvent& event);
    void on_load_trace(wxCommandEvent& event);
    void on_solve_riddle(wxCommandEvent& event)
    {
        std::cout << "Trying to solve riddle";
        zebra::solve_riddle(interact_);
    }
    void OnExit(wxCommandEvent& event);
    void OnAbout(wxCommandEvent& event);

private:
    wxAuiManager aui_manager_;
    zebra::Interact& interact_;
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
        interact.add_listener([this]() {
            this->Refresh();
            this->parse_numbers();
            this->Refresh();
        });
        parse_numbers();
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

    void render_map(wxDC& dc);
    void render_candidates(wxDC& dc);
    void render_numbers(wxDC& dc);

    void render(wxDC& dc);

    wxPoint transform(zebra::Coordinate coord)
    {
        return wxPoint((coord.x + offset_x) * scale, (coord.y + offset_y) * scale);
    }

    zebra::Coordinate transform(wxPoint point)
    {
        return { (point.x / scale) - offset_x, (point.y / scale) - offset_y };
    }

    void parse_numbers()
    {
        parsed_numbers_.clear();

        for (const auto& image : interact_.images())
        {
            zebra::AlienNumberFinder finder(image);

            for (auto point : image)
            {
                if (auto res = finder.find_number_near(point))
                {
                    parsed_numbers_.push_back(*res);
                }
            }
        }
    }

    void mouse_left_up(wxMouseEvent& event)
    {
        interact_(transform(event.GetPosition()));
        Refresh();
    }

    void mouse_right_up(wxMouseEvent& event);

    void mouse_moved(wxMouseEvent& event)
    {
        if (event.Leaving())
        {
            mouse_position_.reset();
        }
        else
        {
            mouse_position_ = transform(event.GetPosition());
        }
        Refresh();
    }

private:
    zebra::Interact& interact_;
    std::optional<zebra::Coordinate> mouse_position_;
    int scale = 5;
    wxCoord offset_x;
    wxCoord offset_y;

    std::vector<zebra::NumberResult> parsed_numbers_;
};

enum
{
    ID_try_all = 1,
    ID_undo = 2,
    ID_save_trace = 3,
    ID_load_trace = 4,
    ID_solve_riddle = 5,
    ID_try_6 = 6,
};
