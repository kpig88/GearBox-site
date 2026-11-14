from bakery import assert_equal
from drafter import *
from dataclasses import dataclass, field
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# DATA CLASSES
# ---------------------------------------------------------

@dataclass
class GearConfiguration:
    """Store the inputs and calculated results for one gear setup."""
    name: str = "My Gear Setup"
    input_rpm: float = 1200.0
    input_teeth: int = 20
    output_teeth: int = 60
    input_torque: float = 10.0
    gear_ratio: float = 3.0
    output_rpm: float = 400.0
    output_torque: float = 30.0
    notes: str = ""


@dataclass
class State:
    """Store information shared between all GearBox pages."""
    configurations: list[GearConfiguration] = field(
        default_factory=list
    )
    current_configuration: GearConfiguration = field(
        default_factory=GearConfiguration
    )
    comparison_mode: bool = False
    graph_type: str = "Output RPM"
    message: str = ""
    notes: str = ""


# ---------------------------------------------------------
# SITE SETTINGS
# ---------------------------------------------------------

set_website_title("GearBox")

set_site_information(
    author="Kathryn Pignatello",
    description=(
        "GearBox is an educational gear ratio calculator "
        "for mechanical engineering students."
    ),
    sources="Drafter documentation and class materials.",
    links=[]
)

set_website_style("water")


# ---------------------------------------------------------
# CALCULATION FUNCTIONS
# ---------------------------------------------------------

def calculate_gear_values(
    input_rpm: float,
    input_teeth: int,
    output_teeth: int,
    input_torque: float
) -> tuple[float, float, float]:
    """Calculate gear ratio, output RPM, and ideal output torque.

    Gear ratio is defined as output teeth divided by input teeth.
    These calculations assume an ideal gear system with no losses.
    """
    gear_ratio = output_teeth / input_teeth
    output_rpm = input_rpm * input_teeth / output_teeth
    output_torque = input_torque * gear_ratio

    return gear_ratio, output_rpm, output_torque


def make_configuration(
    name: str,
    input_rpm: float,
    input_teeth: int,
    output_teeth: int,
    input_torque: float,
    notes: str
) -> GearConfiguration:
    """Create a gear configuration and calculate its results."""
    ratio, rpm, torque = calculate_gear_values(
        input_rpm,
        input_teeth,
        output_teeth,
        input_torque
    )

    return GearConfiguration(
        name=name,
        input_rpm=input_rpm,
        input_teeth=input_teeth,
        output_teeth=output_teeth,
        input_torque=input_torque,
        gear_ratio=ratio,
        output_rpm=rpm,
        output_torque=torque,
        notes=notes
    )


def navigation() -> list:
    """Create the navigation links used on every page."""
    return [
        Header("GearBox"),
        Link("Home", "index"),
        " | ",
        Link("Calculator", "calculator"),
        " | ",
        Link("Results", "results"),
        " | ",
        Link("Compare", "compare"),
        " | ",
        Link("Graphs", "graphs"),
        " | ",
        Link("Saved Setups", "saved_configurations"),
        " | ",
        Link("Gear Guide", "gear_guide"),
        " | ",
        Link("Help", "help"),
        HorizontalRule()
    ]


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@route
def index(state: State) -> Page:
    """Show the GearBox introduction and main navigation."""
    content = navigation() + [
        Header("Welcome to GearBox!"),
        "Learn how gear systems affect rotational speed and torque.",
        "",
        Header("What can you do?"),
        "Use the gear calculator to enter two gear sizes, input RPM, "
        "and input torque.",
        "View the calculated gear ratio, output RPM, and output torque.",
        "Save different gear setups and compare their results.",
        "Use graphs to understand how changing gear sizes affects "
        "a gear system.",
        "",
        Button("Start Calculating", "calculator"),
        Button("Learn About Gears", "gear_guide"),
        "",
        "GearBox is an educational tool. Its calculations assume "
        "ideal gears and are not a substitute for engineering analysis."
    ]

    return Page(state, content)


# ---------------------------------------------------------
# CALCULATOR PAGE
# ---------------------------------------------------------

@route
def calculator(state: State) -> Page:
    """Display the form for entering a new gear configuration."""
    current = state.current_configuration

    content = navigation() + [
        Header("Gear Calculator"),
        "Enter the information about your gear system below.",
        "",
        "Configuration Name:",
        TextBox("name", current.name),
        "",
        "Input RPM:",
        TextBox("input_rpm", str(current.input_rpm), kind="number"),
        "",
        "Driving Gear Teeth:",
        TextBox("input_teeth", str(current.input_teeth), kind="number"),
        "",
        "Driven Gear Teeth:",
        TextBox("output_teeth", str(current.output_teeth), kind="number"),
        "",
        "Input Torque (N·m):",
        TextBox(
            "input_torque",
            str(current.input_torque),
            kind="number"
        ),
        "",
        "Notes about this gear setup:",
        TextArea("notes", current.notes, rows=3),
        "",
        "Enable comparison mode:",
        CheckBox("comparison_mode", state.comparison_mode),
        "",
        Button("Calculate and Save Setup", "calculate"),
        "",
        state.message
    ]

    return Page(state, content)


# ---------------------------------------------------------
# CALCULATE AND SAVE ROUTE
# ---------------------------------------------------------

@route
def calculate(
    state: State,
    name: str,
    input_rpm: str,
    input_teeth: str,
    output_teeth: str,
    input_torque: str,
    notes: str,
    comparison_mode: bool = False
) -> Page:
    """Validate the form, calculate results, and save the setup."""
    # Check for empty inputs before converting them to numbers.
    if (
        name.strip() == ""
        or input_rpm.strip() == ""
        or input_teeth.strip() == ""
        or output_teeth.strip() == ""
        or input_torque.strip() == ""
    ):
        state.message = "Please fill in all required fields."
        return calculator(state)

    # Convert the text inputs into numbers.
    try:
        rpm_value = float(input_rpm)
        input_teeth_value = int(input_teeth)
        output_teeth_value = int(output_teeth)
        torque_value = float(input_torque)
    except ValueError:
        state.message = (
            "Please enter valid numbers. Gear teeth must be whole numbers."
        )
        return calculator(state)

    # Check that values are valid before calculating.
    if (
        rpm_value < 0
        or torque_value < 0
        or input_teeth_value <= 0
        or output_teeth_value <= 0
    ):
        state.message = (
            "RPM and torque cannot be negative. "
            "Gear teeth must be greater than zero."
        )
        return calculator(state)

    # Create the configuration using the helper function.
    new_configuration = make_configuration(
        name,
        rpm_value,
        input_teeth_value,
        output_teeth_value,
        torque_value,
        notes
    )

    # Update multiple State fields.
    state.current_configuration = new_configuration
    state.configurations.append(new_configuration)
    state.comparison_mode = comparison_mode
    state.notes = notes
    state.message = "Your gear configuration was calculated and saved!"

    return results(state)


# ---------------------------------------------------------
# RESULTS PAGE
# ---------------------------------------------------------

@route
def results(state: State) -> Page:
    """Display the current configuration and its calculated results."""
    current = state.current_configuration

    # Explain how the gear ratio affects output speed.
    if current.gear_ratio > 1:
        explanation = (
            "The output gear is larger, so it rotates slower "
            "than the input gear."
        )
    elif current.gear_ratio < 1:
        explanation = (
            "The output gear is smaller, so it rotates faster "
            "than the input gear."
        )
    else:
        explanation = (
            "The gears have the same number of teeth. "
            "This is a 1:1 gear ratio, so their speeds are equal."
        )

    content = navigation() + [
        Header("Calculation Results"),
        "Configuration: " + current.name,
        "",
        Header("Your Inputs"),
        "Input RPM: " + str(current.input_rpm),
        "Driving Gear Teeth: " + str(current.input_teeth),
        "Driven Gear Teeth: " + str(current.output_teeth),
        "Input Torque: " + str(current.input_torque) + " N·m",
        "",
        Header("Calculated Results"),
        "Gear Ratio: " + str(round(current.gear_ratio, 2)) + ":1",
        "Output RPM: " + str(round(current.output_rpm, 2)),
        "Output Torque: " + str(
            round(current.output_torque, 2)
        ) + " N·m",
        "",
        Header("What does this mean?"),
        explanation,
        "For external gears, the output gear also rotates in "
        "the opposite direction.",
        "",
        "These torque calculations assume an ideal system "
        "without friction or other energy losses.",
        "",
        "Notes: " + current.notes,
        "",
        Button("Calculate Another Setup", "calculator"),
        Button("Compare Configurations", "compare"),
        Button("View Graphs", "graphs")
    ]

    return Page(state, content)


# ---------------------------------------------------------
# COMPARISON PAGE
# ---------------------------------------------------------

@route
def compare(state: State) -> Page:
    """Display saved configurations for comparison."""
    content = navigation() + [
        Header("Compare Gear Configurations")
    ]

    # Show a message if there are no saved configurations.
    if len(state.configurations) == 0:
        content.append(
            "You have not saved any gear configurations yet."
        )
        content.append(Button("Create a Setup", "calculator"))

    else:
        if state.comparison_mode:
            content.append(
                "Comparison mode is enabled. Here are your saved setups:"
            )
        else:
            content.append(
                "Comparison mode is currently disabled. "
                "Turn it on in the calculator to compare setups."
            )

        # This loop retrieves the results from every saved setup.
        for configuration in state.configurations:
            content.append(Header(configuration.name))
            content.append(
                "Gear Ratio: "
                + str(round(configuration.gear_ratio, 2))
                + ":1"
            )
            content.append(
                "Output RPM: "
                + str(round(configuration.output_rpm, 2))
            )
            content.append(
                "Output Torque: "
                + str(round(configuration.output_torque, 2))
                + " N·m"
            )
            content.append(HorizontalRule())

        content.append(
            Button("Turn Comparison Mode On", "enable_comparison")
        )
        content.append(
            Button("Turn Comparison Mode Off", "disable_comparison")
        )

    content.append(Button("Create Another Setup", "calculator"))

    return Page(state, content)


@route
def enable_comparison(state: State) -> Page:
    """Turn comparison mode on."""
    state.comparison_mode = True
    return compare(state)


@route
def disable_comparison(state: State) -> Page:
    """Turn comparison mode off."""
    state.comparison_mode = False
    return compare(state)


# ---------------------------------------------------------
# GRAPHS PAGE
# ---------------------------------------------------------

@route
def graphs(state: State) -> Page:
    """Display a graph based on the saved gear configurations."""
    content = navigation() + [
        Header("Graphs and Visualization"),
        "Choose which result you want to compare:",
        SelectBox(
            "graph_type",
            ["Gear Ratio", "Output RPM", "Output Torque"],
            state.graph_type
        ),
        Button("Update Graph", "choose_graph"),
        ""
    ]

    # A graph requires at least one saved configuration.
    if len(state.configurations) == 0:
        content.append(
            "Save at least one gear configuration to create a graph."
        )
        content.append(Button("Go to Calculator", "calculator"))

    else:
        labels = []
        values = []

        # Loop through saved configurations to generate graph data.
        for configuration in state.configurations:
            labels.append(configuration.name)

            if state.graph_type == "Gear Ratio":
                values.append(configuration.gear_ratio)
            elif state.graph_type == "Output RPM":
                values.append(configuration.output_rpm)
            else:
                values.append(configuration.output_torque)

        # Matplotlib creates a bar graph from the saved data.
        plt.figure(figsize=(8, 4))
        plt.bar(labels, values, color="steelblue")
        plt.title(state.graph_type + " Comparison")
        plt.xlabel("Gear Configurations")
        plt.ylabel(state.graph_type)
        plt.xticks(rotation=20)
        plt.tight_layout()

        content.append(MatPlotLibPlot())

        content.append(
            "This graph compares the selected result across "
            "your saved gear configurations."
        )

    return Page(state, content)


@route
def choose_graph(state: State, graph_type: str) -> Page:
    """Update the selected graph type."""
    state.graph_type = graph_type
    return graphs(state)


# ---------------------------------------------------------
# SAVED CONFIGURATIONS PAGE
# ---------------------------------------------------------

@route
def saved_configurations(state: State) -> Page:
    """Display all configurations saved during the current session."""
    content = navigation() + [
        Header("Saved Configurations")
    ]

    if len(state.configurations) == 0:
        content.append(
            "You have not saved any configurations yet."
        )
    else:
        # Display every saved configuration.
        for configuration in state.configurations:
            content.append(Header(configuration.name))
            content.append(
                "Input Gear Teeth: "
                + str(configuration.input_teeth)
            )
            content.append(
                "Output Gear Teeth: "
                + str(configuration.output_teeth)
            )
            content.append(
                "Gear Ratio: "
                + str(round(configuration.gear_ratio, 2))
                + ":1"
            )
            content.append(
                "Output RPM: "
                + str(round(configuration.output_rpm, 2))
            )
            content.append(
                "Output Torque: "
                + str(round(configuration.output_torque, 2))
                + " N·m"
            )
            content.append("Notes: " + configuration.notes)
            content.append(HorizontalRule())

        content.append(
            Button("Clear All Configurations", "clear_configurations")
        )

    content.append(Button("Create Another Setup", "calculator"))

    return Page(state, content)


@route
def clear_configurations(state: State) -> Page:
    """Remove all saved configurations from the current session."""
    state.configurations.clear()
    state.current_configuration = GearConfiguration()
    state.comparison_mode = False
    state.message = "All saved configurations have been cleared."

    return saved_configurations(state)


# ---------------------------------------------------------
# GEAR GUIDE PAGE
# ---------------------------------------------------------

@route
def gear_guide(state: State) -> Page:
    """Teach users the basic concepts of gear systems."""
    content = navigation() + [
        Header("Learn About Gears"),
        Header("What is a gear?"),
        "A gear is a rotating mechanical part with teeth. "
        "Two gears can connect together to transfer motion and torque.",
        "",
        Header("Driving Gear"),
        "The driving gear is the gear that provides the input motion.",
        "",
        Header("Driven Gear"),
        "The driven gear is the gear that receives motion from "
        "the driving gear.",
        "",
        Header("Gear Ratio"),
        "Gear ratio = Driven Gear Teeth / Driving Gear Teeth",
        "",
        Header("Output RPM"),
        "Output RPM = Input RPM × Driving Gear Teeth "
        "/ Driven Gear Teeth",
        "",
        Header("Output Torque"),
        "Ideal Output Torque = Input Torque × Gear Ratio",
        "",
        Header("Example"),
        "Imagine a 20-tooth driving gear connected to a "
        "60-tooth driven gear.",
        "The gear ratio is 60 / 20 = 3:1.",
        "If the input speed is 1200 RPM, the output speed "
        "is 400 RPM.",
        "If the input torque is 10 N·m, the ideal output "
        "torque is 30 N·m.",
        "",
        "The larger output gear rotates slower but produces "
        "more ideal torque.",
        "",
        Button("Try the Calculator", "calculator")
    ]

    return Page(state, content)


# ---------------------------------------------------------
# HELP PAGE
# ---------------------------------------------------------

@route
def help(state: State) -> Page:
    """Explain how to use the GearBox website."""
    content = navigation() + [
        Header("Help and Instructions"),
        "1. Open the Gear Calculator.",
        "2. Enter a name for your gear configuration.",
        "3. Enter the input RPM and input torque.",
        "4. Enter the number of teeth on the driving and "
        "driven gears.",
        "5. Add notes if you want to remember what you tested.",
        "6. Select comparison mode if you want to compare "
        "multiple setups.",
        "7. Press Calculate and Save Setup.",
        "8. Visit Results to see your calculations.",
        "9. Visit Compare to review multiple configurations.",
        "10. Visit Graphs to visualize your results.",
        "",
        Header("Important Information"),
        "RPM and torque cannot be negative. Gear tooth counts "
        "must be positive whole numbers.",
        "GearBox assumes an ideal gear system without friction "
        "or other energy losses.",
        "Saved configurations are stored in the current app "
        "session. They are not permanently stored in a database.",
        "",
        Button("Go to Calculator", "calculator")
    ]

    return Page(state, content)


# ---------------------------------------------------------
# BASIC UNIT TESTS
# ---------------------------------------------------------

# These tests check the calculation helper using a known example.
# Page routes are also tested manually by using each page and form
# in the running website, since they depend on Drafter components.

def test_calculations() -> None:
    """Check that the gear calculation function gives correct results."""
    ratio, rpm, torque = calculate_gear_values(
        1200.0,
        20,
        60,
        10.0
    )

    assert ratio == 3.0
    assert rpm == 400.0
    assert torque == 30.0

    ratio, rpm, torque = calculate_gear_values(
        1000.0,
        40,
        20,
        5.0
    )

    assert ratio == 0.5
    assert rpm == 2000.0
    assert torque == 2.5



test_calculations()


# ---------------------------------------------------------
# START THE WEBSITE
# ---------------------------------------------------------
hide_debug_information()
start_server(State())
