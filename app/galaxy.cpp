#include <algorithm>
#include <iostream>

#include <wx/wx.h>

#include <nitro/lang/enumerate.hpp>
#include <nitro/lang/reverse.hpp>

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
: wxFrame(NULL, wxID_ANY, "Hello World", wxDefaultPosition, wxSize(1024, 768),
          wxDEFAULT_FRAME_STYLE)
{
    wxMenu* menuFile = new wxMenu;
    menuFile->Append(ID_Hello, "&Hello...\tCtrl-H",
                     "Help string shown in status bar for this menu item");
    menuFile->AppendSeparator();
    menuFile->Append(wxID_EXIT);
    wxMenu* menuHelp = new wxMenu;
    menuHelp->Append(wxID_ABOUT);
    wxMenuBar* menuBar = new wxMenuBar;
    menuBar->Append(menuFile, "&File");
    menuBar->Append(menuHelp, "&Help");
    SetMenuBar(menuBar);
    CreateStatusBar();
    SetStatusText("Welcome to wxWidgets!");
    Bind(wxEVT_MENU, &GalaxyFrame::OnHello, this, ID_Hello);
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
void GalaxyFrame::OnHello(wxCommandEvent& event)
{
    wxLogMessage("Hello world from wxWidgets!");
}

GalaxyDC::GalaxyDC(GalaxyPanel* dp) : wxAutoBufferedPaintDC(dp)
{
    // SetAxisOrientation(true, true);
    // SetLogicalOrigin(0, 0);
    SetBackground(*wxWHITE_BRUSH);
}

void GalaxyPanel::bounding_box(wxDC& dc)
{
    wxCoord min_x = 0, min_y = 0, max_x = 0, max_y = 0;
    for (const auto& image : interact_.images)
    {
        for (const auto& pixel : image)
        {
            min_x = std::min<wxCoord>(min_x, pixel.x);
            max_x = std::max<wxCoord>(max_x, pixel.x);
            min_y = std::min<wxCoord>(min_y, pixel.y);
            max_y = std::max<wxCoord>(max_y, pixel.y);
        }
    }
    wxCoord size_x = max_x - min_x + 1;
    wxCoord size_y = max_y - min_y + 1;
    offset_x = -min_x;
    offset_y = -min_y;

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

void GalaxyPanel::render(wxDC& dc)
{
    bounding_box(dc);

    if (scale > 6)
    {
        dc.SetPen(*wxGREY_PEN);
    }
    else
    {
        dc.SetPen(wxNullPen);
    }

    for (const auto& elem : nitro::lang::enumerate(nitro::lang::reverse(interact_.images)))
    {
        int grayscale = (255 / interact_.images.size()) * (elem.index() + 1);
        dc.SetBrush(wxBrush(wxColor(grayscale, grayscale, grayscale)));

        for (const auto& pixel : elem.value())
        {
            dc.DrawRectangle(transform(pixel), wxSize(scale, scale));
        }
    }

    dc.SetPen(*wxGREEN_PEN);
    dc.SetBrush(wxNullBrush);
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
