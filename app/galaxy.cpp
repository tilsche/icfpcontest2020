#include <algorithm>
#include <iostream>

#include <wx/wx.h>

#include <nitro/lang/enumerate.hpp>
#include <nitro/lang/reverse.hpp>

#include "alien.hpp"
#include "eval.hpp"
#include "interact.hpp"

#include "galaxy.hpp"

BEGIN_EVENT_TABLE(GalaxyPanel, wxPanel)
// some useful events
/*
 EVT_LEFT_UP(ChartDrawPanel::mouseReleased)
 EVT_RIGHT_DOWN(ChartDrawPanel::rightClick)
 EVT_LEAVE_WINDOW(ChartDrawPanel::mouseLeftWindow)
 */
// EVT_MOUSEWHEEL(ChartDrawPanel::mouseWheelMoved)
// EVT_LEFT_DOWN(ChartDrawPanel::mouseDown)
EVT_LEFT_UP(GalaxyPanel::mouse_left_up)
EVT_RIGHT_UP(GalaxyPanel::mouse_right_up)
EVT_MOTION(GalaxyPanel::mouse_moved)
// EVT_KEY_DOWN(ChartDrawPanel::keyPressed)
// EVT_KEY_UP(ChartDrawPanel::keyReleased)
//// catch paint events
EVT_PAINT(GalaxyPanel::paint_event)
// EVT_TIMER(Chart_AnimationTimer, ChartDrawPanel::animationTimer)
END_EVENT_TABLE()

wxIMPLEMENT_APP(GalaxyApp);
bool GalaxyApp::OnInit()
{
    interact_.evaluator.add_function_file("../resources/galaxy.txt");
    interact_({ 0, 0 });
    interact_({ 0, 0 });
    interact_({ 0, 0 });
    interact_({ 0, 0 });
    interact_({ 0, 0 });
    interact_({ 0, 0 });
    interact_({ 0, 0 });
    interact_({ 0, 0 });

    interact_({ 0, 0 });
    interact_({ 8, 4 });
    interact_({ 2, -8 });
    interact_({ 3, 6 });
    interact_({ 0, -14 });
    interact_({ -4, 10 });
    interact_({ 9, -3 });
    interact_({ -4, 10 });
    interact_({ 1, 4 });

    GalaxyFrame* frame = new GalaxyFrame(interact_);
    frame->Show(true);
    return true;
}
GalaxyFrame::GalaxyFrame(zebra::Interact& interact)
: wxFrame(NULL, wxID_ANY, "Hello Galaxy", wxDefaultPosition, wxSize(1024, 768),
          wxDEFAULT_FRAME_STYLE),
  interact_(interact)
{
    wxMenu* menuFile = new wxMenu;
    menuFile->Append(ID_try_all, "Try all!");
    menuFile->Append(ID_undo, "Undo (ctrl-z)\tCtrl+z");
    menuFile->AppendSeparator();
    menuFile->Append(wxID_EXIT);
    wxMenu* menuHelp = new wxMenu;
    menuHelp->Append(wxID_ABOUT);
    wxMenuBar* menuBar = new wxMenuBar;
    menuBar->Append(menuFile, "&File");
    menuBar->Append(menuHelp, "&Help");
    SetMenuBar(menuBar);
    CreateStatusBar();
    SetStatusText("Welcome to the Galaxy!");
    Bind(wxEVT_MENU, &GalaxyFrame::on_try_all, this, ID_try_all);
    Bind(wxEVT_MENU, &GalaxyFrame::on_undo, this, ID_undo);
    Bind(wxEVT_MENU, &GalaxyFrame::OnAbout, this, wxID_ABOUT);
    Bind(wxEVT_MENU, &GalaxyFrame::OnExit, this, wxID_EXIT);

    aui_manager_.SetManagedWindow(this);

    auto galaxy_panel = new GalaxyPanel(this, interact);

    aui_manager_.AddPane(galaxy_panel, wxAuiPaneInfo().CenterPane());
    aui_manager_.Update();
}
void GalaxyFrame::OnExit(wxCommandEvent& event)
{
    Close(true);
}

void GalaxyFrame::OnAbout(wxCommandEvent& event)
{
    wxMessageBox("This is a wxWidgets Hello World example", "About Hello World",
                 wxOK | wxICON_INFORMATION);
}

void GalaxyFrame::on_try_all(wxCommandEvent& event)
{
    interact_.try_all();
}

void GalaxyFrame::on_undo(wxCommandEvent& event)
{
    interact_.undo();
}

GalaxyDC::GalaxyDC(GalaxyPanel* dp) : wxAutoBufferedPaintDC(dp)
{
    // SetAxisOrientation(true, true);
    // SetLogicalOrigin(0, 0);
    SetBackground(*wxWHITE_BRUSH);
}

void GalaxyPanel::bounding_box(wxDC& dc)
{
    auto [top_left, bottom_right] = zebra::bounding_box(interact_.images());
    wxCoord size_x = bottom_right.x - top_left.x + 1;
    wxCoord size_y = bottom_right.y - top_left.y + 1;
    offset_x = -top_left.x;
    offset_y = -top_left.y;

    scale = std::min<int>(dc.GetSize().x / size_x, dc.GetSize().y / size_y);
    if (scale < 1)
    {
        // Try to make bigger
        SetSize(wxSize(size_x, size_y));
        scale = 1;
    }

    dc.SetPen(wxNullPen);
    dc.SetBrush(*wxBLACK_BRUSH);
    dc.DrawRectangle(wxPoint(0, 0), scale * wxSize(size_x, size_y));
}

void GalaxyPanel::mouse_right_up(wxMouseEvent& event)
{
    auto point = transform(event.GetPosition());

    for (const auto& image : interact_.images())
    {
        zebra::AlienNumberFinder finder(image);
        auto res = finder.find_number_near(point);

        if (res)
        {
            parsed_numbers_.push_back(*res);
            return;
        }
    }

    Refresh();
}

void GalaxyPanel::render_candidates(wxDC& dc)
{
    static std::vector<wxBrushStyle> candidate_brush_styles = {
        wxBRUSHSTYLE_BDIAGONAL_HATCH, wxBRUSHSTYLE_CROSSDIAG_HATCH,  wxBRUSHSTYLE_FDIAGONAL_HATCH,
        wxBRUSHSTYLE_CROSS_HATCH,     wxBRUSHSTYLE_HORIZONTAL_HATCH, wxBRUSHSTYLE_VERTICAL_HATCH,
    };

    for (const auto& elem : nitro::lang::enumerate(interact_.candidates))
    {
        auto index = elem.index();
        const auto& candidate = elem.value();
        int cweight = 100 + (155 / interact_.candidates.size() * (index + 1));
        const auto& bs = candidate_brush_styles[index % candidate_brush_styles.size()];
        if (std::get<0>(candidate.first))
        {
            if (scale > 6)
            {
                dc.SetPen(*wxRED_PEN);
            }
            else
            {
                dc.SetPen(wxNullPen);
            }
            dc.SetBrush(wxBrush(wxColor(cweight, 0, 0), bs));
        }
        else
        {
            if (scale > 6)
            {
                dc.SetPen(*wxBLUE_PEN);
            }
            else
            {
                dc.SetPen(wxNullPen);
            }
            dc.SetBrush(wxBrush(wxColor(0, 0, cweight), bs));
        }
        for (const auto& pixel : candidate.second)
        {
            dc.DrawRectangle(transform(pixel), wxSize(scale, scale));
        }
    }
}

void GalaxyPanel::render_numbers(wxDC& dc)
{
    dc.SetBrush(wxNullBrush);
    dc.SetPen(wxPen(wxColor(255, 0, 255)));
    auto fontsize = std::max(10, std::min(48, 4 * this->scale));
    dc.SetFont(wxFont(fontsize, wxFONTFAMILY_MODERN, wxFONTSTYLE_NORMAL, wxFONTWEIGHT_BOLD));
    dc.SetTextForeground(wxColor(0, 255, 255));

    for (auto& parsed_number : parsed_numbers_)
    {

        dc.DrawRectangle(transform(parsed_number.pivot), parsed_number.size * wxSize(scale, scale));

        dc.DrawText(std::to_string(parsed_number.number), transform(parsed_number.pivot));
    }
}

void GalaxyPanel::render_map(wxDC& dc)
{
    if (scale > 6)
    {
        dc.SetPen(*wxGREY_PEN);
    }
    else
    {
        dc.SetPen(wxNullPen);
    }

    for (const auto& elem : nitro::lang::enumerate(nitro::lang::reverse(interact_.images())))
    {
        int grayscale = (255 / interact_.images().size()) * (elem.index() + 1);
        dc.SetBrush(wxBrush(wxColor(grayscale, grayscale, grayscale)));

        for (const auto& pixel : elem.value())
        {
            dc.DrawRectangle(transform(pixel), wxSize(scale, scale));
        }
    }
}

void GalaxyPanel::render(wxDC& dc)
{
    bounding_box(dc);

    render_map(dc);
    render_candidates(dc);
    render_numbers(dc);

    dc.SetPen(*wxGREEN_PEN);
    if (mouse_position_)
    {
        dc.DrawRectangle(transform(*mouse_position_), wxSize(scale, scale));
    }
}

//
// int main()
//{
//    zebra::Interact i("galaxy");
//    i.evaluator.add_function_file("../resources/galaxy.txt");
//
//    i({ 0, 0 });
//    i({ 0, 0 });
//    i({ 0, 0 });
//    i({ 0, 0 });
//    i({ 0, 0 });
//    i({ 0, 0 });
//    i({ 0, 0 });
//    i({ 0, 0 });
//    i({ 0, 0 });
//    i({ 8, 4 });
//    i({ 2, -8 });
//    i({ 3, 6 });
//    i({ 0, -14 });
//    i({ -4, 10 });
//    i({ 9, -3 });
//    i({ -4, 10 });
//    i({ 1, 4 });
//    i({ -78, 13 });
//    i({ -7, 13 });
//    i({ 1, 1 });
//    //
//    //    std::cout << e.eval(zebra::parse_expr("ap inc 4")) << "\n";
//    //    std::cout << e.eval(zebra::parse_expr("ap pwr2 4")) << "\n";
//}
