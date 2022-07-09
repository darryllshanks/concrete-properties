import pytest
import numpy as np

from concreteproperties.material import Concrete, Steel
from concreteproperties.concrete_section import ConcreteSection
from concreteproperties.stress_strain_profile import (
    ConcreteLinear,
    RectangularStressBlock,
    SteelElasticPlastic,
)

from sectionproperties.pre.library.concrete_sections import concrete_rectangular_section


# generate list of angles to test
thetas = np.linspace(start=-np.pi, stop=np.pi, num=31)

# define material properties
concrete = Concrete(
    name="40 MPa Concrete",
    density=2.4e-6,
    stress_strain_profile=ConcreteLinear(elastic_modulus=32.8e3),
    ultimate_stress_strain_profile=RectangularStressBlock(
        compressive_strength=40,
        alpha=0.85,
        gamma=0.77,
        ultimate_strain=0.003,
    ),
    alpha_squash=0.85,
    flexural_tensile_strength=0.6 * np.sqrt(40),
    colour="lightgrey",
)

steel = Steel(
    name="500 MPa Steel",
    density=7.85e-6,
    stress_strain_profile=SteelElasticPlastic(
        yield_strength=500,
        elastic_modulus=200e3,
        fracture_strain=0.05,
    ),
    colour="grey",
)

# reference geometry
ref_geom = concrete_rectangular_section(
    b=400,
    d=600,
    dia_top=20,
    n_top=3,
    dia_bot=20,
    n_bot=3,
    n_circle=4,
    cover=30,
    area_top=310,
    area_bot=310,
    conc_mat=concrete,
    steel_mat=steel,
)

ref_sec = ConcreteSection(ref_geom)
ref_gross_results = ref_sec.gross_properties
ref_cracked = ref_sec.calculate_cracked_properties()


@pytest.mark.parametrize("theta", thetas)
def test_rotated_gross_properties(theta):
    # rotate reference geometry
    new_geom = ref_geom.rotate_section(angle=theta, use_radians=True)
    new_sec = ConcreteSection(new_geom)
    new_gross_results = new_sec.gross_properties

    assert pytest.approx(new_gross_results.total_area) == ref_gross_results.total_area
    assert (
        pytest.approx(new_gross_results.concrete_area)
        == ref_gross_results.concrete_area
    )
    assert pytest.approx(new_gross_results.steel_area) == ref_gross_results.steel_area
    assert pytest.approx(new_gross_results.e_a) == ref_gross_results.e_a
    assert pytest.approx(new_gross_results.mass) == ref_gross_results.mass
    assert pytest.approx(new_gross_results.perimeter) == ref_gross_results.perimeter
    assert pytest.approx(new_gross_results.e_qx) == ref_gross_results.e_qx
    assert pytest.approx(new_gross_results.e_qy) == ref_gross_results.e_qy
    assert pytest.approx(new_gross_results.cx) == ref_gross_results.cx
    assert pytest.approx(new_gross_results.cy) == ref_gross_results.cy
    assert pytest.approx(new_gross_results.e_i11) == ref_gross_results.e_i11
    assert pytest.approx(new_gross_results.e_i22) == ref_gross_results.e_i22
    assert pytest.approx(new_gross_results.e_z11_plus) == ref_gross_results.e_z11_plus
    assert pytest.approx(new_gross_results.e_z11_minus) == ref_gross_results.e_z11_minus
    assert pytest.approx(new_gross_results.e_z22_plus) == ref_gross_results.e_z22_plus
    assert pytest.approx(new_gross_results.e_z22_minus) == ref_gross_results.e_z22_minus
    assert pytest.approx(new_gross_results.squash_load) == ref_gross_results.squash_load
    assert (
        pytest.approx(new_gross_results.tensile_load) == ref_gross_results.tensile_load
    )
    assert pytest.approx(new_gross_results.axial_pc_x) == ref_gross_results.axial_pc_x
    assert pytest.approx(new_gross_results.axial_pc_y) == ref_gross_results.axial_pc_y


@pytest.mark.parametrize("theta", thetas)
def test_rotated_cracked_properties(theta):
    # rotate reference geometry
    new_geom = ref_geom.rotate_section(angle=theta, use_radians=True)
    new_sec = ConcreteSection(new_geom)
    new_cracked = new_sec.calculate_cracked_properties(theta=theta)

    assert pytest.approx(new_cracked.m_cr) == ref_cracked.m_cr
    assert pytest.approx(new_cracked.d_nc) == ref_cracked.d_nc
    assert pytest.approx(new_cracked.e_a_cr) == ref_cracked.e_a_cr
    assert pytest.approx(new_cracked.e_iuu_cr) == ref_cracked.e_iuu_cr


# list of normal forces
normal_forces = [-1e3, 0, 1e3, 1e5]


@pytest.mark.parametrize("theta", thetas)
def test_rotated_ultimate_properties(theta):
    # rotate reference geometry
    new_geom = ref_geom.rotate_section(angle=theta, use_radians=True)
    new_sec = ConcreteSection(new_geom)

    for nf in normal_forces:
        ref_ultimate = ref_sec.ultimate_bending_capacity(n=nf)
        new_ultimate = new_sec.ultimate_bending_capacity(theta=theta, n=nf)

        assert pytest.approx(new_ultimate.d_n) == ref_ultimate.d_n
        assert pytest.approx(new_ultimate.mv) == ref_ultimate.mv


# list of normal forces
normal_forces = [-1e3, 0, 1e3, 1e5]


@pytest.mark.parametrize("theta", thetas)
def test_rotated_uncracked_stress(theta):
    # rotate reference geometry
    new_geom = ref_geom.rotate_section(angle=theta, use_radians=True)
    new_sec = ConcreteSection(new_geom)

    # determine moments
    m = 10e6
    mx = m * np.cos(theta)
    my = -m * np.sin(theta)

    for nf in normal_forces:
        ref_uncr_stress = ref_sec.calculate_uncracked_stress(n=nf, mx=m)
        new_uncr_stress = new_sec.calculate_uncracked_stress(n=nf, mx=mx, my=my)

        for idx, cf in enumerate(new_uncr_stress.concrete_forces):
            assert pytest.approx(cf[0]) == ref_uncr_stress.concrete_forces[idx][0]
            assert pytest.approx(cf[1]) == ref_uncr_stress.concrete_forces[idx][1]

        for idx, sf in enumerate(new_uncr_stress.steel_forces):
            assert pytest.approx(sf[0]) == ref_uncr_stress.steel_forces[idx][0]
            assert pytest.approx(sf[1]) == ref_uncr_stress.steel_forces[idx][1]


# list of normal forces
normal_forces = [-1e3, 0, 1e3, 1e5]


@pytest.mark.parametrize("theta", thetas)
def test_rotated_cracked_stress(theta):
    # rotate reference geometry
    new_geom = ref_geom.rotate_section(angle=theta, use_radians=True)
    new_sec = ConcreteSection(new_geom)
    new_cracked = new_sec.calculate_cracked_properties(theta=theta)

    # determine moments
    m = 100e6

    for nf in normal_forces:
        ref_cr_stress = ref_sec.calculate_cracked_stress(
            cracked_results=ref_cracked, n=nf, m=m
        )
        new_cr_stress = new_sec.calculate_cracked_stress(
            cracked_results=new_cracked, n=nf, m=m
        )

        for idx, cf in enumerate(new_cr_stress.concrete_forces):
            assert pytest.approx(cf[0]) == ref_cr_stress.concrete_forces[idx][0]
            assert pytest.approx(cf[1]) == ref_cr_stress.concrete_forces[idx][1]

        for idx, sf in enumerate(new_cr_stress.steel_forces):
            assert pytest.approx(sf[0]) == ref_cr_stress.steel_forces[idx][0]
            assert pytest.approx(sf[1]) == ref_cr_stress.steel_forces[idx][1]


# list of normal forces
normal_forces = [-1e3, 0, 1e3, 1e5]


@pytest.mark.parametrize("theta", thetas)
def test_rotated_ultimate_stress(theta):
    # rotate reference geometry
    new_geom = ref_geom.rotate_section(angle=theta, use_radians=True)
    new_sec = ConcreteSection(new_geom)

    for nf in normal_forces:
        ref_ultimate = ref_sec.ultimate_bending_capacity(n=nf)
        new_ultimate = new_sec.ultimate_bending_capacity(theta=theta, n=nf)

        ref_ult_stress = ref_sec.calculate_ultimate_stress(
            ultimate_results=ref_ultimate
        )
        new_ult_stress = new_sec.calculate_ultimate_stress(
            ultimate_results=new_ultimate
        )

        for idx, cf in enumerate(new_ult_stress.concrete_forces):
            assert pytest.approx(cf[0]) == ref_ult_stress.concrete_forces[idx][0]
            assert pytest.approx(cf[1]) == ref_ult_stress.concrete_forces[idx][1]

        for idx, sf in enumerate(new_ult_stress.steel_forces):
            assert pytest.approx(sf[0]) == ref_ult_stress.steel_forces[idx][0]
            assert pytest.approx(sf[1]) == ref_ult_stress.steel_forces[idx][1]
