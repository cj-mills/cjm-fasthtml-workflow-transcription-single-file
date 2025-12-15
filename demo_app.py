"""Demo application for cjm-fasthtml-workflow-transcription-single-file library.

This demo showcases the self-contained single-file transcription workflow:

1. SingleFileTranscriptionWorkflow:
   - Fully self-contained workflow with internal plugin registry
   - Resource management for GPU/CPU availability checks
   - Background job management with SSE streaming
   - Media file discovery, mounting, and browsing
   - Result storage and persistence

2. StepFlow Integration:
   - Plugin selection step (shows all discovered transcription plugins)
   - File selection step (paginated media browser)
   - Confirmation step (review and start transcription)

3. Media Library:
   - Directory scanning for audio/video files
   - Paginated browsing with grid/list views
   - File preview modal with media player
   - Configurable file filters and sorting

4. Result Storage:
   - Auto-save transcription results to JSON
   - Configurable results directory
   - Export to multiple formats (TXT, SRT, VTT)

Run without transcription plugins installed to test the "no plugins" scenario,
then install plugins (e.g., cjm-transcription-plugin-*) to test full functionality.
"""

from pathlib import Path


def main():
    """Main entry point - initializes workflow and starts the server."""
    from fasthtml.common import fast_app, Div, H1, P, Span, A, Code, APIRouter
    from cjm_fasthtml_daisyui.core.resources import get_daisyui_headers
    from cjm_fasthtml_daisyui.core.testing import create_theme_persistence_script
    from cjm_fasthtml_sse.helpers import insert_htmx_sse_ext
    from cjm_fasthtml_app_core.components.navbar import create_navbar
    from cjm_fasthtml_app_core.core.routing import register_routes
    from cjm_fasthtml_app_core.core.htmx import handle_htmx_request
    from cjm_fasthtml_app_core.core.layout import wrap_with_layout
    from cjm_fasthtml_app_core.core.html_ids import AppHtmlIds

    # Import styling utilities
    from cjm_fasthtml_tailwind.utilities.spacing import p, m
    from cjm_fasthtml_tailwind.utilities.sizing import container, max_w
    from cjm_fasthtml_tailwind.utilities.typography import font_size, font_weight, text_align
    from cjm_fasthtml_tailwind.core.base import combine_classes
    from cjm_fasthtml_daisyui.components.actions.button import btn, btn_colors, btn_sizes
    from cjm_fasthtml_daisyui.components.data_display.badge import badge, badge_colors
    from cjm_fasthtml_daisyui.components.feedback.alert import alert, alert_colors, alert_styles

    print("\n" + "="*70)
    print("Initializing cjm-fasthtml-workflow-transcription-single-file Demo")
    print("="*70)

    # Import workflow components
    from cjm_fasthtml_workflow_transcription_single_file.workflow.workflow import SingleFileTranscriptionWorkflow

    print("  Library components imported successfully")

    # Create the FastHTML app
    app, rt = fast_app(
        pico=False,
        hdrs=[
            *get_daisyui_headers(),
            create_theme_persistence_script(),
        ],
        title="Single-File Transcription Workflow Demo",
        htmlkw={'data-theme': 'light'},
        secret_key="your-secret-key-here"
    )

    router = APIRouter(prefix="")

    # Add HTMX SSE extension for Server-Sent Events support
    insert_htmx_sse_ext(app.hdrs)

    print("  FastHTML app created successfully")

    # Create the single-file transcription workflow using the convenience method
    # The workflow is fully self-contained and manages its own:
    # - UnifiedPluginRegistry (discovers transcription plugins)
    # - ResourceManager (GPU/CPU availability)
    # - TranscriptionJobManager (background job execution)
    # - SSEBroadcastManager (event streaming)
    # - MediaLibrary (file discovery and browsing)
    # - ResultStorage (transcription persistence)
    #
    # Configuration is automatically loaded from saved settings files
    # (configs/workflows/single_file/settings.json) with dataclass defaults
    # for any missing values. Only route-specific overrides needed here.
    print("\n[1/2] Creating and setting up SingleFileTranscriptionWorkflow...")

    single_file_workflow = SingleFileTranscriptionWorkflow.create_and_setup(
        app,
        route_prefix="/workflow",
        no_plugins_redirect="/",  # Redirect to home if no plugins configured
    )

    print("  Workflow created and setup complete")

    # Store workflow in app.state for access from routes
    app.state.single_file_workflow = single_file_workflow

    # Check plugin status
    plugins = single_file_workflow.plugin_registry.get_configured_plugins()
    all_plugins = single_file_workflow.plugin_registry.get_all_plugins()
    print(f"\n  Discovered plugins: {len(all_plugins)}")
    print(f"  Configured plugins: {len(plugins)}")

    if all_plugins:
        for plugin in all_plugins:
            status = "configured" if plugin.is_configured else "not configured"
            print(f"    - {plugin.title} ({status})")

    # Define routes
    @router
    def index(request):
        """Homepage with workflow overview and entry point."""

        def home_content():
            # Get current plugin status
            all_plugins = single_file_workflow.plugin_registry.get_all_plugins()
            configured_plugins = single_file_workflow.plugin_registry.get_configured_plugins()
            media_files = single_file_workflow.media_library.scan()

            return Div(
                H1("Single-File Transcription Workflow Demo",
                   cls=combine_classes(font_size._4xl, font_weight.bold, m.b(4))),

                P("A self-contained workflow for transcribing audio and video files:",
                  cls=combine_classes(font_size.lg, m.b(6))),

                # Feature list
                Div(
                    Div(
                        Span("", cls=combine_classes(font_size._2xl, m.r(3))),
                        Span("Plugin-based transcription engine support"),
                        cls=combine_classes(m.b(3))
                    ),
                    Div(
                        Span("", cls=combine_classes(font_size._2xl, m.r(3))),
                        Span("Media file discovery with paginated browsing"),
                        cls=combine_classes(m.b(3))
                    ),
                    Div(
                        Span("", cls=combine_classes(font_size._2xl, m.r(3))),
                        Span("3-step wizard: Plugin -> File -> Confirm"),
                        cls=combine_classes(m.b(3))
                    ),
                    Div(
                        Span("", cls=combine_classes(font_size._2xl, m.r(3))),
                        Span("Background job execution with SSE progress"),
                        cls=combine_classes(m.b(3))
                    ),
                    Div(
                        Span("", cls=combine_classes(font_size._2xl, m.r(3))),
                        Span("Auto-save results with export options"),
                        cls=combine_classes(m.b(8))
                    ),
                    cls=combine_classes(text_align.left, m.b(8))
                ),

                # Status badges
                Div(
                    Span(
                        Span(f"{len(all_plugins)}", cls=str(font_weight.bold)),
                        " Discovered",
                        cls=combine_classes(
                            badge,
                            badge_colors.info if all_plugins else badge_colors.warning,
                            m.r(2)
                        )
                    ),
                    Span(
                        Span(f"{len(configured_plugins)}", cls=str(font_weight.bold)),
                        " Configured",
                        cls=combine_classes(
                            badge,
                            badge_colors.success if configured_plugins else badge_colors.error,
                            m.r(2)
                        )
                    ),
                    Span(
                        Span(f"{len(media_files)}", cls=str(font_weight.bold)),
                        " Media Files",
                        cls=combine_classes(
                            badge,
                            badge_colors.success if media_files else badge_colors.warning
                        )
                    ),
                    cls=combine_classes(m.b(8))
                ),

                # Action buttons
                Div(
                    A(
                        "Start Transcription Workflow",
                        href="/workflow",
                        cls=combine_classes(btn, btn_colors.primary, btn_sizes.lg, m.r(2))
                    ),
                    A(
                        "View Workflow Settings",
                        href="/workflow/settings",
                        cls=combine_classes(btn, btn_colors.secondary, btn_sizes.lg)
                    ) if hasattr(single_file_workflow, 'settings_url') else None,
                ),

                # Info message if no plugins
                Div(
                    Div(
                        Span("Info: ", cls=str(font_weight.bold)),
                        "No transcription plugins discovered. Install a plugin package ",
                        "(e.g., ", Code("pip install cjm-transcription-plugin-*"), ") ",
                        "and restart the demo to enable transcription.",
                        cls=combine_classes(alert, alert_colors.info, m.t(8))
                    )
                ) if not all_plugins else None,

                # Info message if no media directories
                Div(
                    Div(
                        Span("Note: ", cls=str(font_weight.bold)),
                        "No media directories configured. Use the workflow settings ",
                        "to add directories containing audio/video files to transcribe.",
                        cls=combine_classes(alert, alert_colors.warning, m.t(4))
                    )
                ) if not media_files else None,

                cls=combine_classes(
                    container,
                    max_w._4xl,
                    m.x.auto,
                    p(8),
                    text_align.center
                )
            )

        return handle_htmx_request(
            request,
            home_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )


    @router
    def workflow(request, sess):
        """Render the transcription workflow."""

        def workflow_content():
            return Div(
                single_file_workflow.render_entry_point(request, sess),
                cls=combine_classes(container, max_w._6xl, m.x.auto, p(4))
            )

        return handle_htmx_request(
            request,
            workflow_content,
            wrap_fn=lambda content: wrap_with_layout(content, navbar=navbar)
        )

    # Create navbar (after routes are defined so we can reference them)
    navbar = create_navbar(
        title="Transcription Demo",
        nav_items=[
            ("Home", index),
            ("Workflow", workflow),
        ],
        home_route=index,
        theme_selector=True
    )

    # Register all routes
    print("\n[2/2] Registering routes...")
    register_routes(
        app,
        router,
        *single_file_workflow.get_routers()
    )

    # Debug: Print registered routes
    print("\n" + "="*70)
    print("Registered Routes:")
    print("="*70)
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  {route.path}")

    print("\n" + "="*70)
    print("Demo App Ready!")
    print("="*70)
    print("\n Library Components:")
    print("  - SingleFileTranscriptionWorkflow - Main workflow orchestrator")
    print("  - SingleFileWorkflowConfig - Workflow configuration")
    print("  - MediaConfig - Media scanning settings")
    print("  - StorageConfig - Result storage settings")
    print("  - MediaLibrary - File discovery and browsing")
    print("  - ResultStorage - Transcription persistence")
    print("  - PluginRegistryAdapter - Plugin integration")
    print("  - StepFlow integration - 3-step wizard")
    print("="*70 + "\n")

    return app


if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading

    # Call main to initialize everything and get the app
    app = main()

    def open_browser(url):
        print(f"Opening browser at {url}")
        webbrowser.open(url)

    port = 5030
    host = "0.0.0.0"
    display_host = 'localhost' if host in ['0.0.0.0', '127.0.0.1'] else host

    print(f"Server: http://{display_host}:{port}")
    print("\nAvailable routes:")
    print(f"  http://{display_host}:{port}/          - Homepage with status")
    print(f"  http://{display_host}:{port}/workflow  - Transcription workflow")
    print("\n" + "="*70 + "\n")

    # Open browser after a short delay
    timer = threading.Timer(1.5, lambda: open_browser(f"http://localhost:{port}"))
    timer.daemon = True
    timer.start()

    # Start server
    uvicorn.run(app, host=host, port=port)
